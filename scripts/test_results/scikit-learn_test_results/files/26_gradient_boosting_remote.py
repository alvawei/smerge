"""Gradient Boosting methods

This module contains methods for fitting gradient boosted regression trees for
both classification and regression.

The module structure is the following:

- The ``BaseGradientBoosting`` base class implements a common ``fit`` method
  for all the estimators in the module. Regression and classification
  only differ the the concrete ``LossFunction`` used.

- ``GradientBoostingClassifier`` implements gradient boosting for
  classification problems.

- ``GradientBoostingRegressor`` implements gradient boosting for
  classification problems.
"""

# Authors: Peter Prettenhofer, Scott White, Gilles Louppe
# License: BSD Style.

from __future__ import division
from abc import ABCMeta, abstractmethod

import numpy as np

from .base import BaseEnsemble
from ..base import ClassifierMixin
from ..base import RegressorMixin
from ..utils import check_random_state, array2d

from ..tree.tree import Tree
from ..tree._tree import _find_best_split
from ..tree._tree import _random_sample_mask
from ..tree._tree import _apply_tree
from ..tree._tree import MSE
from ..tree._tree import DTYPE

from ._gradient_boosting import predict_stages
from ._gradient_boosting import predict_stage

__all__ = ["GradientBoostingClassifier",
           "GradientBoostingRegressor"]


class MedianEstimator(object):
    """An estimator predicting the median of the training targets."""
    def fit(self, X, y):
        self.median = np.median(y)

    def predict(self, X):
        y = np.empty((X.shape[0], 1), dtype=np.float64)
        y.fill(self.median)
        return y


class MeanEstimator(object):
    """An estimator predicting the mean of the training targets."""
    def fit(self, X, y):
        self.mean = np.mean(y)

    def predict(self, X):
        y = np.empty((X.shape[0], 1), dtype=np.float64)
        y.fill(self.mean)
        return y


class LogOddsEstimator(object):
    """An estimator predicting the log odds ratio."""
    def fit(self, X, y):
        n_pos = np.sum(y)
        self.prior = np.log(n_pos / (y.shape[0] - n_pos))

    def predict(self, X):
        y = np.empty((X.shape[0], 1), dtype=np.float64)
        y.fill(self.prior)
        return y


class PriorProbabilityEstimator(object):
    """An estimator predicting the probability of each
    class in the training data.
    """
    def fit(self, X, y):
        class_counts = np.bincount(y)
        self.priors = class_counts / float(y.shape[0])

    def predict(self, X):
        y = np.empty((X.shape[0], self.priors.shape[0]), dtype=np.float64)
        y[:] = self.priors
        return y


class LossFunction(object):
    """Abstract base class for various loss functions.

    Attributes
    ----------
    K : int
        The number of regression trees to be induced;
        1 for regression and binary classification;
        ``n_classes`` for multi-class classification.
    """
    __metaclass__ = ABCMeta

    is_multi_class = False

    def __init__(self, n_classes):
        self.K = n_classes

    def init_estimator(self, X, y):
        raise NotImplementedError()

    @abstractmethod
    def __call__(self, y, pred):
        """Compute the loss of prediction ``pred`` and ``y``. """

    @abstractmethod
    def negative_gradient(self, y, y_pred, **kargs):
        """Compute the negative gradient.

        Parameters
        ---------
        y : np.ndarray, shape=(n,)
            The target labels.
        y_pred : np.ndarray, shape=(n,):
            The predictions.
        """

    def update_terminal_regions(self, tree, X, y, residual, y_pred,
                                sample_mask, learn_rate=1.0, k=0):
        """Update the terminal regions (=leaves) of the given tree and
        updates the current predictions of the model. Traverses tree
        and invokes template method `_update_terminal_region`.

        Parameters
        ----------
        tree : tree.Tree
            The tree object.
        X : np.ndarray, shape=(n, m)
            The data array.
        y : np.ndarray, shape=(n,)
            The target labels.
        residual : np.ndarray, shape=(n,)
            The residuals (usually the negative gradient).
        y_pred : np.ndarray, shape=(n,):
            The predictions.
        """
        # compute leaf for each sample in ``X``.
        terminal_regions = np.empty((X.shape[0], ), dtype=np.int32)
        _apply_tree(X, tree.children, tree.feature, tree.threshold,
                    terminal_regions)

        # mask all which are not in sample mask.
        masked_terminal_regions = terminal_regions.copy()
        masked_terminal_regions[~sample_mask] = -1

        # update each leaf (= perform line search)
        for leaf in np.where(tree.children[:, 0] == Tree.LEAF)[0]:
            self._update_terminal_region(tree, masked_terminal_regions,
                                         leaf, X, y, residual,
                                         y_pred[:, k])

        # update predictions (both in-bag and out-of-bag)
        y_pred[:, k] += learn_rate * tree.value[:, 0].take(terminal_regions,
                                                           axis=0)

    @abstractmethod
    def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                                residual, pred):
        """Template method for updating terminal regions (=leaves). """


class RegressionLossFunction(LossFunction):
    """Base class for regression loss functions. """
    __metaclass__ = ABCMeta

    def __init__(self, n_classes):
        if n_classes != 1:
            raise ValueError("``n_classes`` must be 1 for regression")
        super(RegressionLossFunction, self).__init__(n_classes)


class LeastSquaresError(RegressionLossFunction):
    """Loss function for least squares (LS) estimation.
    Terminal regions need not to be updated for least squares. """
    def init_estimator(self):
        return MeanEstimator()

    def __call__(self, y, pred):
        return np.mean((y - pred.ravel()) ** 2.0)

    def negative_gradient(self, y, pred, **kargs):
        return y - pred.ravel()

    def update_terminal_regions(self, tree, X, y, residual, y_pred,
                                sample_mask, learn_rate=1.0, k=0):
        """Least squares does not need to update terminal regions.

        But it has to update the predictions.
        """
        # update predictions
        y_pred[:, k] += learn_rate * tree.predict(X).ravel()

    def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                                residual, pred):
        pass


class LeastAbsoluteError(RegressionLossFunction):
    """Loss function for least absolute deviation (LAD) regression. """
    def init_estimator(self):
        return MedianEstimator()

    def __call__(self, y, pred):
        return np.abs(y - pred.ravel()).mean()

    def negative_gradient(self, y, pred, **kargs):
        return np.sign(y - pred.ravel())

    def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                                residual, pred):
        """LAD updates terminal regions to median estimates. """
        terminal_region = np.where(terminal_regions == leaf)[0]
        tree.value[leaf, 0] = np.median(y.take(terminal_region, axis=0) - \
                                        pred.take(terminal_region, axis=0))


class BinomialDeviance(LossFunction):
    """Binomial deviance loss function for binary classification.

    Binary classification is a special case; here, we only need to
    fit one tree instead of ``n_classes`` trees.
    """
    def __init__(self, n_classes):
        if n_classes != 2:
            raise ValueError("%s requires 2 classes." %
                             self.__class__.__name__)
        # we only need to fit one tree for binary clf.
        super(BinomialDeviance, self).__init__(1)

    def init_estimator(self):
        return LogOddsEstimator()

    def __call__(self, y, pred):
        """Compute the deviance (= negative log-likelihood). """
        # logaddexp(0, v) == log(1.0 + exp(v))
        pred = pred.ravel()
        return np.sum(np.logaddexp(0.0, -2 * y * pred)) / y.shape[0]

    def negative_gradient(self, y, pred, **kargs):
        return y - 1.0 / (1.0 + np.exp(-pred.ravel()))

    def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                                residual, pred):
        """Make a single Newton-Raphson step. """
        terminal_region = np.where(terminal_regions == leaf)[0]
        residual = residual.take(terminal_region, axis=0)
        y = y.take(terminal_region, axis=0)

        numerator = residual.sum()
        denominator = np.sum((y - residual) * (1 - y + residual))

        if denominator == 0.0:
            tree.value[leaf, 0] = 0.0
        else:
            tree.value[leaf, 0] = numerator / denominator


class MultinomialDeviance(LossFunction):
    """Multinomial deviance loss function for multi-class classification.

    For multi-class classification we need to fit ``n_classes`` trees at
    each stage.
    """

    is_multi_class = True

    def __init__(self, n_classes):
        if n_classes < 3:
            raise ValueError("%s requires more than 2 classes."
                             % self.__class__.__name__)
        super(MultinomialDeviance, self).__init__(n_classes)

    def init_estimator(self):
        return PriorProbabilityEstimator()

    def __call__(self, y, pred):
        # create one-hot label encoding
        Y = np.zeros((y.shape[0], self.K), dtype=np.float64)
        for k in range(self.K):
            Y[:, k] = y == k

        return np.sum(-1 * (Y * pred).sum(axis=1) +
                      np.log(np.exp(pred).sum(axis=1)))

    def negative_gradient(self, y, pred, k=0):
        """Compute negative gradient for the ``k``-th class. """
        return y - np.exp(pred[:, k]) / np.sum(np.exp(pred), axis=1)

    def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                                residual, pred):
        """Make a single Newton-Raphson step. """
        terminal_region = np.where(terminal_regions == leaf)[0]
        residual = residual.take(terminal_region, axis=0)

        y = y.take(terminal_region, axis=0)

        numerator = residual.sum()
        numerator *= (self.K - 1) / self.K

        denominator = np.sum((y - residual) * (1.0 - y + residual))

        if denominator == 0.0:
            tree.value[leaf, 0] = 0.0
        else:
            tree.value[leaf, 0] = numerator / denominator


LOSS_FUNCTIONS = {'ls': LeastSquaresError,
                  'lad': LeastAbsoluteError,
                  'bdeviance': BinomialDeviance,
                  'mdeviance': MultinomialDeviance,
                  'deviance': None}  # for both, multinomial and binomial


class BaseGradientBoosting(BaseEnsemble):
    """Abstract base class for Gradient Boosting. """
    def __init__(self, loss, learn_rate, n_estimators, min_samples_split,
                 min_samples_leaf, max_depth, init, subsample, random_state):
        if n_estimators <= 0:
            raise ValueError("n_estimators must be greater than 0")
        self.n_estimators = n_estimators

        if learn_rate <= 0.0:
            raise ValueError("learn_rate must be greater than 0")
        self.learn_rate = learn_rate

        if loss not in LOSS_FUNCTIONS:
            raise ValueError("Loss '%s' not supported. " % loss)
        self.loss = loss

        if min_samples_split <= 0:
            raise ValueError("min_samples_split must be larger than 0.")
        self.min_samples_split = min_samples_split

        if min_samples_leaf <= 0:
            raise ValueError("min_samples_leaf must be larger than 0.")
        self.min_samples_leaf = min_samples_leaf

        if subsample <= 0.0 or subsample > 1:
            raise ValueError("subsample must be in (0,1]")
        self.subsample = subsample

        if max_depth <= 0:
            raise ValueError("max_depth must be larger than 0.")
        self.max_depth = max_depth

        if init is not None:
            if not hasattr(init, 'fit') or not hasattr(init, 'predict'):
                raise ValueError("init must be valid estimator")
        self.init = init

        self.random_state = check_random_state(random_state)

        self.estimators_ = None

    def fit_stage(self, i, X, X_argsorted, y, y_pred, sample_mask):
        """Fit another stage of ``n_classes_`` trees to the boosting model. """
        loss = self.loss_
        original_y = y

        for k in range(loss.K):
            if loss.is_multi_class:
                y = np.array(original_y == k, dtype=np.float64)

            residual = loss.negative_gradient(y, y_pred, k=k)

            # induce regression tree on residuals
            tree = Tree(1, self.n_features)
            tree.build(X, residual, MSE(), self.max_depth,
                       self.min_samples_split, self.min_samples_leaf, 0.0,
                       self.n_features, self.random_state, _find_best_split,
                       sample_mask, X_argsorted)

            # update tree leaves
            self.loss_.update_terminal_regions(tree, X, y, residual, y_pred,
                                               sample_mask, self.learn_rate,
                                               k=k)

            # add tree to ensemble
            self.estimators_[i, k] = tree

        return y_pred

    def fit(self, X, y):
        """Fit the gradient boosting model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features. Use fortran-style
            to avoid memory copies.

        y : array-like, shape = [n_samples]
            Target values (integers in classification, real numbers in
            regression)
            For classification, labels must correspond to classes
            ``0, 1, ..., n_classes_-1``

        Returns
        -------
        self : object
            Returns self.
        """
        X = np.asfortranarray(X, dtype=DTYPE)
        y = np.ascontiguousarray(y)

        n_samples, n_features = X.shape
        if y.shape[0] != n_samples:
            raise ValueError("Number of labels does not match " \
                             "number of samples.")
        self.n_features = n_features

        loss = LOSS_FUNCTIONS[self.loss](self.n_classes_)

        # store loss object for future use
        self.loss_ = loss

        if self.init is None:
            self.init = loss.init_estimator()

        # create argsorted X for fast tree induction
        X_argsorted = np.asfortranarray(
            np.argsort(X.T, axis=1).astype(np.int32).T)

        # fit initial model
        self.init.fit(X, y)

        # init predictions
        y_pred = self.init.predict(X)

        self.estimators_ = np.empty((self.n_estimators, loss.K),
                                    dtype=np.object)

        self.train_score_ = np.zeros((self.n_estimators,), dtype=np.float64)
        self.oob_score_ = np.zeros((self.n_estimators), dtype=np.float64)

        sample_mask = np.ones((n_samples,), dtype=np.bool)
        n_inbag = max(1, int(self.subsample * n_samples))

        # perform boosting iterations
        for i in range(self.n_estimators):

            # subsampling
            if self.subsample < 1.0:
                # TODO replace with ``np.choice`` if possible.
                sample_mask = _random_sample_mask(n_samples, n_inbag,
                                                  self.random_state)

            # fit next stage of trees
            y_pred = self.fit_stage(i, X, X_argsorted, y, y_pred, sample_mask)

            # track deviance (= loss)
            if self.subsample < 1.0:
                self.train_score_[i] = loss(y[sample_mask],
                                            y_pred[sample_mask])
                self.oob_score_[i] = loss(y[~sample_mask],
                                          y_pred[~sample_mask])
            else:
                # no need to fancy index w/ no subsampling
                self.train_score_[i] = loss(y, y_pred)

        return self

    def _make_estimator(self, append=True):
        # we don't need _make_estimator
        raise NotImplementedError()

    @property
    def feature_importances_(self):
        if self.estimators_ is None or len(self.estimators_) == 0:
            raise ValueError("Estimator not fitted, " \
                             "call `fit` before `feature_importances_`.")
        total_sum = np.zeros((self.n_features, ), dtype=np.float64)
        for stage in self.estimators_:
            stage_sum = sum(tree.compute_feature_importances(method='squared')
                            for tree in stage) / len(stage)
            total_sum += stage_sum

        importances = total_sum / len(self.estimators_)
        return importances

    def staged_decision_function(self, X):
        """Compute decision function for X.

        This method allows monitoring (i.e. determine error on testing set)
        after each stage.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        f : array of shape = [n_samples, n_classes]
            The decision function of the input samples. Classes are
            ordered by arithmetical order. Regression and binary
            classification are special cases with ``n_classes == 1``.
        """
        X = array2d(X, dtype=DTYPE, order='C')

        if self.estimators_ is None or len(self.estimators_) == 0:
            raise ValueError("Estimator not fitted, call `fit` " \
                             "before `staged_decision_function`.")
        if X.shape[1] != self.n_features:
            raise ValueError("X.shape[1] should be %d, not %d." %
                             (self.n_features, X.shape[1]))

        score = self.init.predict(X).astype(np.float64)

        for i in range(self.n_estimators):
            predict_stage(self.estimators_, i, X, self.learn_rate, score)
            yield score


class GradientBoostingClassifier(BaseGradientBoosting, ClassifierMixin):
    """Gradient Boosting for classification.

    GB builds an additive model in a
    forward stage-wise fashion; it allows for the optimization of
    arbitrary differentiable loss functions. In each stage ``n_classes_``
    regression trees are fit on the negative gradient of the
    binomial or multinomial deviance loss function. Binary classification
    is a special case where only a single regression tree is induced.

    Parameters
    ----------
    loss : {'deviance', 'ls'}, optional (default='deviance')
        loss function to be optimized. 'deviance' refers to
        deviance (= logistic regression) for classification
        with probabilistic outputs. 'ls' refers to least squares
        regression.

    learn_rate : float, optional (default=0.1)
        learning rate shrinks the contribution of each tree by `learn_rate`.
        There is a trade-off between learn_rate and n_estimators.

    n_estimators : int (default=100)
        The number of boosting stages to perform. Gradient boosting
        is fairly robust to over-fitting so a large number usually
        results in better performance.

    max_depth : integer, optional (default=3)
        maximum depth of the individual regression estimators. The maximum
        depth limits the number of nodes in the tree. Tune this parameter
        for best performance; the best value depends on the interaction
        of the input variables.

    min_samples_split : integer, optional (default=1)
        The minimum number of samples required to split an internal node.

    min_samples_leaf : integer, optional (default=1)
        The minimum number of samples required to be at a leaf node.

    subsample : float, optional (default=1.0)
        The fraction of samples to be used for fitting the individual base
        learners. If smaller than 1.0 this results in Stochastic Gradient
        Boosting. `subsample` interacts with the parameter `n_estimators`.

    Examples
    --------
    >>> samples = [[0, 0, 2], [1, 0, 0]]
    >>> labels = [0, 1]
    >>> from sklearn.ensemble import GradientBoostingClassifier
    >>> gb = GradientBoostingClassifier().fit(samples, labels)
    >>> print gb.predict([[0.5, 0, 0]])
    [0]

    See also
    --------
    sklearn.tree.DecisionTreeClassifier, RandomForestClassifier

    References
    ----------
    J. Friedman, Greedy Function Approximation: A Gradient Boosting
    Machine, The Annals of Statistics, Vol. 29, No. 5, 2001.

    J. Friedman, Stochastic Gradient Boosting, 1999

    T. Hastie, R. Tibshirani and J. Friedman.
    Elements of Statistical Learning Ed. 2, Springer, 2009.
    """

    def __init__(self, loss='deviance', learn_rate=0.1, n_estimators=100,
                 subsample=1.0, min_samples_split=1, min_samples_leaf=1,
                 max_depth=3, init=None, random_state=None):

        super(GradientBoostingClassifier, self).__init__(
            loss, learn_rate, n_estimators, min_samples_split,
            min_samples_leaf, max_depth, init, subsample, random_state)

    def fit(self, X, y):
        """Fit the gradient boosting model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features. Use fortran-style
            to avoid memory copies.

        y : array-like, shape = [n_samples]
            Target values (integers in classification, real numbers in
            regression)
            For classification, labels must correspond to classes
            ``0, 1, ..., n_classes_-1``

        Returns
        -------
        self : object
            Returns self.
        """
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        y = np.searchsorted(self.classes_, y)
        if self.loss == 'deviance':
            self.loss = 'mdeviance' if len(self.classes_) > 2 else 'bdeviance'

        return super(GradientBoostingClassifier, self).fit(X, y)

    def predict(self, X):
        """Predict class for X.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y : array of shape = [n_samples]
            The predicted classes.
        """
        probas = self.predict_proba(X)
        return self.classes_.take(np.argmax(probas, axis=1), axis=0)

    def predict_proba(self, X):
        """Predict class probabilities for X.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        p : array of shape = [n_samples]
            The class probabilities of the input samples. Classes are
            ordered by arithmetical order.
        """
        X = array2d(X, dtype=DTYPE, order='C')

        if self.estimators_ is None or len(self.estimators_) == 0:
            raise ValueError("Estimator not fitted, " \
                             "call `fit` before `predict_proba`.")
        if X.shape[1] != self.n_features:
            raise ValueError("X.shape[1] should be %d, not %d." %
                             (self.n_features, X.shape[1]))

        proba = np.ones((X.shape[0], self.n_classes_), dtype=np.float64)

        score = self.init.predict(X).astype(np.float64)
        predict_stages(self.estimators_, X, self.learn_rate, score)

        if not self.loss_.is_multi_class:
            proba[:, 1] = 1.0 / (1.0 + np.exp(-score.ravel()))
            proba[:, 0] -= proba[:, 1]
        else:
            proba = np.exp(score) / np.sum(np.exp(score), axis=1)[:, np.newaxis]
        return proba


class GradientBoostingRegressor(BaseGradientBoosting, RegressorMixin):
    """Gradient Boosting for regression.

    GB builds an additive model in a forward stage-wise fashion;
    it allows for the optimization of arbitrary differentiable loss functions.
    In each stage a regression tree is fit on the negative gradient of the
    given loss function.

    Parameters
    ----------
    loss : {'ls', 'lad'}, optional (default='ls')
        loss function to be optimized. 'ls' refers to least squares
        regression. 'lad' (least absolute deviation) is a highly robust
        loss function soley based on order information of the input
        variables.

    learn_rate : float, optional (default=0.1)
        learning rate shrinks the contribution of each tree by `learn_rate`.
        There is a trade-off between learn_rate and n_estimators.

    n_estimators : int (default=100)
        The number of boosting stages to perform. Gradient boosting
        is fairly robust to over-fitting so a large number usually
        results in better performance.

    max_depth : integer, optional (default=3)
        maximum depth of the individual regression estimators. The maximum
        depth limits the number of nodes in the tree. Tune this parameter
        for best performance; the best value depends on the interaction
        of the input variables.

    min_samples_split : integer, optional (default=1)
        The minimum number of samples required to split an internal node.

    min_samples_leaf : integer, optional (default=1)
        The minimum number of samples required to be at a leaf node.

    subsample : float, optional (default=1.0)
        The fraction of samples to be used for fitting the individual base
        learners. If smaller than 1.0 this results in Stochastic Gradient
        Boosting. `subsample` interacts with the parameter `n_estimators`.

    Attributes
    ----------
    `feature_importances_` : array, shape = [n_features]
        The feature importances (the higher, the more important the feature).

    `oob_score_` : array, shape = [n_estimators]
        Score of the training dataset obtained using an out-of-bag estimate.
        The i-th score ``oob_score_[i]`` is the deviance (= loss) of the
        model at iteration ``i`` on the out-of-bag sample.

    `train_score_` : array, shape = [n_estimators]
        The i-th score ``train_score_[i]`` is the deviance (= loss) of the
        model at iteration ``i`` on the in-bag sample.
        If ``subsample == 1`` this is the deviance on the training data.

    Attributes
    ----------
    `feature_importances_` : array, shape = [n_features]
        The feature importances (the higher, the more important the feature).

    `oob_score_` : array, shape = [n_estimators]
        Score of the training dataset obtained using an out-of-bag estimate.
        The i-th score ``oob_score_[i]`` is the deviance (= loss) of the
        model at iteration ``i`` on the out-of-bag sample.

    `train_score_` : array, shape = [n_estimators]
        The i-th score ``train_score_[i]`` is the deviance (= loss) of the
        model at iteration ``i`` on the in-bag sample.
        If ``subsample == 1`` this is the deviance on the training data.

    Examples
    --------
    >>> samples = [[0, 0, 2], [1, 0, 0]]
    >>> labels = [0, 1]
    >>> from sklearn.ensemble import GradientBoostingRegressor
    >>> gb = GradientBoostingRegressor().fit(samples, labels)
    >>> print gb.predict([[0, 0, 0]])    # doctest: +ELLIPSIS
    [  1.32806997e-05]

    See also
    --------
    sklearn.tree.DecisionTreeRegressor, RandomForestRegressor

    References
    ----------
    J. Friedman, Greedy Function Approximation: A Gradient Boosting
    Machine, The Annals of Statistics, Vol. 29, No. 5, 2001.

    J. Friedman, Stochastic Gradient Boosting, 1999

    T. Hastie, R. Tibshirani and J. Friedman.
    Elements of Statistical Learning Ed. 2, Springer, 2009.
    """

    def __init__(self, loss='ls', learn_rate=0.1, n_estimators=100,
                 subsample=1.0, min_samples_split=1, min_samples_leaf=1,
                 max_depth=3, init=None, random_state=None):

        super(GradientBoostingRegressor, self).__init__(
            loss, learn_rate, n_estimators, min_samples_split,
            min_samples_leaf, max_depth, init, subsample, random_state)

    def fit(self, X, y):
        """Fit the gradient boosting model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features. Use fortran-style
            to avoid memory copies.

        y : array-like, shape = [n_samples]
            Target values (integers in classification, real numbers in
            regression)
            For classification, labels must correspond to classes
            ``0, 1, ..., n_classes_-1``

        Returns
        -------
        self : object
            Returns self.
        """
        self.n_classes_ = 1
        return super(GradientBoostingRegressor, self).fit(X, y)

    def predict(self, X):
        """Predict regression target for X.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y: array of shape = [n_samples]
            The predicted values.
        """
        X = array2d(X, dtype=DTYPE, order='C')

        if self.estimators_ is None or len(self.estimators_) == 0:
            raise ValueError("Estimator not fitted, " \
                             "call `fit` before `predict`.")
        if X.shape[1] != self.n_features:
            raise ValueError("X.shape[1] should be %d, not %d." %
                             (self.n_features, X.shape[1]))

        y = self.init.predict(X).astype(np.float64)
        predict_stages(self.estimators_, X, self.learn_rate, y)
        return y.ravel()

    def staged_predict(self, X):
        """Predict regression target at each stage for X.

        This method allows monitoring (i.e. determine error on testing set)
        after each stage.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y : array of shape = [n_samples]
            The predicted value of the input samples.
        """
        X = array2d(X, dtype=DTYPE, order='C')
        for y in self.staged_decision_function(X):
            yield y.ravel()
