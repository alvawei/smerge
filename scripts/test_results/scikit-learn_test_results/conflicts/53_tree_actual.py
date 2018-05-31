"""
This module gathers tree-based methods, including decision, regression and
randomized trees.
"""
# Code is originally adapted from MILK: Machine Learning Toolkit
# Authors: Brian Holt, Peter Prettenhofer, Satrajit Ghosh, Gilles Louppe
# License: BSD3
from __future__ import division
from __future__ import division
import numpy as np
import numpy as np
from ..base import BaseEstimator, ClassifierMixin, RegressorMixin
from ..base import BaseEstimator, ClassifierMixin, RegressorMixin
from ..utils import array2d, check_random_state
from ..utils import array2d, check_random_state
from . import _tree
from . import _tree


class Tree(object):
<<<<<<< REMOTE
def _build_tree(X, y, is_classification, criterion, max_depth, min_split,
                min_density, max_features, random_state, n_classes, find_split,
                sample_mask=None, X_argsorted=None):
    """Build a tree by recursively partitioning the data."""

    if max_depth <= 10:
        init_capacity = (2 ** (max_depth + 1)) - 1
    else:
        init_capacity = 2047  # num nodes of tree with depth 10

    tree = Tree(n_classes, init_capacity)

    # Recursively partition X
    def recursive_partition(X, X_argsorted, y, sample_mask, depth,
                            parent, is_left_child):
        # Count samples
        n_node_samples = sample_mask.sum()

        if n_node_samples == 0:
            raise ValueError("Attempting to find a split "
                             "with an empty sample_mask")

        # Split samples
        if depth < max_depth and n_node_samples >= min_split:
            feature, threshold, best_error, init_error = find_split(
                X, y, X_argsorted, sample_mask, n_node_samples,
                max_features, criterion, random_state)

        else:
            feature = -1

        # Value at this node
        current_y = y[sample_mask]

        if is_classification:
            value = np.zeros((n_classes,))
            t = current_y.max() + 1
            value[:t] = np.bincount(current_y.astype(np.int))

        else:
            value = np.asarray(np.mean(current_y))

        # Terminal node
        if feature == -1:
            # compute error at leaf
            error = _tree._error_at_leaf(y, sample_mask, criterion,
                                         n_node_samples)
            tree.add_leaf(parent, is_left_child, value, error, n_node_samples)

        # Internal node
        else:
            # Sample mask is too sparse?
            if n_node_samples / X.shape[0] <= min_density:
                X = X[sample_mask]
                X_argsorted = np.asfortranarray(
                    np.argsort(X.T, axis=1).astype(np.int32).T)
                y = current_y
                sample_mask = np.ones((X.shape[0],), dtype=np.bool)

            # Split and and recurse
            split = X[:, feature] <= threshold

            node_id = tree.add_split_node(parent, is_left_child, feature,
                                          threshold, best_error, init_error,
                                          n_node_samples, value)

            # left child recursion
            recursive_partition(X, X_argsorted, y,
                                split & sample_mask,
                                depth + 1, node_id, True)

            # right child recursion
            recursive_partition(X, X_argsorted, y,
                                ~split & sample_mask,
                                depth + 1, node_id, False)

    # Launch the construction
    if X.dtype != DTYPE or not np.isfortran(X):
        X = np.asanyarray(X, dtype=DTYPE, order="F")

    if y.dtype != DTYPE or not y.flags.contiguous:
        y = np.ascontiguousarray(y, dtype=DTYPE)

    if sample_mask is None:
        sample_mask = np.ones((X.shape[0],), dtype=np.bool)

    if X_argsorted is None:
        X_argsorted = np.asfortranarray(
            np.argsort(X.T, axis=1).astype(np.int32).T)

    recursive_partition(X, X_argsorted, y, sample_mask, 0, -1, False)

    tree.resize(tree.node_count)
    return tree



=======
def _build_tree(X, y, is_classification, criterion, max_depth, min_split,
                min_density, max_features, random_state, n_classes, find_split,
                sample_mask=None, X_argsorted=None, store_terminal_region=False):
    """Build a tree by recursively partitioning the data."""

    # Convert input format
    if X.dtype != DTYPE or not np.isfortran(X):
        X = np.asanyarray(X, dtype=DTYPE, order="F")

    if y.dtype != DTYPE or not y.flags.contiguous:
        y = np.ascontiguousarray(y, dtype=DTYPE)

    # create sample mask and preprocess inputs
    if sample_mask is None:
        sample_mask = np.ones((X.shape[0],), dtype=np.bool)

    if X_argsorted is None:
        X_argsorted = np.asfortranarray(
            np.argsort(X.T, axis=1).astype(np.int32).T)

    # create tree structure
    if max_depth <= 10:
        init_capacity = (2 ** (max_depth + 1)) - 1
    else:
        init_capacity = 2047  # num nodes of tree with depth 10

    tree = Tree(n_classes, init_capacity)

    # init terminal region if necessary
    if store_terminal_region:
        if min_density != 0.0:
            raise ValueError(
                "If min_density has to be 0.0 if store_terminal_region")
        tree.terminal_region = np.empty((X.shape[0], ), dtype=np.int32)
        tree.terminal_region.fill(-1)

    # Recursively partition X
    def recursive_partition(X, X_argsorted, y, sample_mask, depth,
                            parent, is_left_child):
        # Count samples
        n_node_samples = sample_mask.sum()

        if n_node_samples == 0:
            raise ValueError("Attempting to find a split "
                             "with an empty sample_mask")

        # Split samples
        if depth < max_depth and n_node_samples >= min_split:
            feature, threshold, best_error, init_error = find_split(
                X, y, X_argsorted, sample_mask, n_node_samples,
                max_features, criterion, random_state)

        else:
            feature = -1

        # Value at this node
        current_y = y[sample_mask]

        if is_classification:
            value = np.zeros((n_classes,))
            t = current_y.max() + 1
            value[:t] = np.bincount(current_y.astype(np.int))

        else:
            value = np.asarray(np.mean(current_y))

        # Terminal node
        if feature == -1:
            # compute error at leaf
            error = _tree._error_at_leaf(y, sample_mask, criterion,
                                         n_node_samples)
            node_id = tree.add_leaf(parent, is_left_child, value, error,
                                    n_node_samples)
            if store_terminal_region:
                tree.terminal_region[sample_mask] = node_id

        # Internal node
        else:
            # Sample mask is too sparse?
            if n_node_samples / X.shape[0] <= min_density:
                X = X[sample_mask]
                X_argsorted = np.asfortranarray(
                    np.argsort(X.T, axis=1).astype(np.int32).T)
                y = current_y
                sample_mask = np.ones((X.shape[0],), dtype=np.bool)

            # Split and and recurse
            split = X[:, feature] <= threshold

            node_id = tree.add_split_node(parent, is_left_child, feature,
                                          threshold, best_error, init_error,
                                          n_node_samples, value)

            # left child recursion
            recursive_partition(X, X_argsorted, y,
                                split & sample_mask,
                                depth + 1, node_id, True)

            # right child recursion
            recursive_partition(X, X_argsorted, y,
                                ~split & sample_mask,
                                depth + 1, node_id, False)

    recursive_partition(X, X_argsorted, y, sample_mask, 0, -1, False)

    tree.resize(tree.node_count)
    return tree



>>>>>>> LOCAL
class BaseDecisionTree(BaseEstimator):
    """Base class for decision trees.

    Warning: This class should not be used directly.
    Use derived classes instead.
    """
    def __init__(self, criterion,
                       max_depth,
                       min_split,
                       min_density,
                       max_features,
                       random_state):
    def predict(self, X):
    def fit(self, X, y):
        """Build a decision tree from the training set (X, y).

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The training input samples.

        y : array-like, shape = [n_samples]
            The target values (integers that correspond to classes in
            classification, real numbers in regression).

        Return
        ------
        self : object
            Returns self.
        """
        # Convert data
        X = np.asarray(X, dtype=DTYPE, order='F')

        is_classification = isinstance(self, ClassifierMixin)

        else:

        # Check parameters
        if self.max_depth is not None and self.max_depth <= 0:
        if self.max_features >= 0 and \
               not (0 < self.max_features <= self.n_features):
        # Build tree


        return self
class DecisionTreeClassifier(BaseDecisionTree, ClassifierMixin):
    """A decision tree classifier.

    Parameters
    ----------
    criterion : string, optional (default="gini")
        The function to measure the quality of a split. Supported criteria are
        "gini" for the Gini impurity and "entropy" for the information gain.

    max_depth : integer or None, optional (default=10)
        The maximum depth of the tree. If None, then nodes are expanded until
        all leaves are pure or until all leaves contain less than min_split
        samples.

    min_split : integer, optional (default=1)
        The minimum number of samples required to split an internal node.

    min_density : float, optional (default=0.1)
        The minimum density of the `sample_mask` (i.e. the fraction of samples
        in the mask). If the density falls below this threshold the mask is
        recomputed and the input data is packed which results in data copying.
        If `min_density` equals to one, the partitions are always represented
        as copies of the original data. Otherwise, partitions are represented
        as bit masks (aka sample masks).

    max_features : int or None, optional (default=None)
        The number of features to consider when looking for the best split.
        If None, all features are considered, otherwise max_features are chosen
        at random.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Decision_tree_learning

    .. [2] L. Breiman, J. Friedman, R. Olshen, and C. Stone, "Classification
           and Regression Trees", Wadsworth, Belmont, CA, 1984.

    .. [3] T. Hastie, R. Tibshirani and J. Friedman. "Elements of Statistical
           Learning", Springer, 2009.

    See also
    --------
    DecisionTreeRegressor

    Examples
    --------
    >>> from sklearn.datasets import load_iris
    >>> from sklearn.cross_validation import cross_val_score
    >>> from sklearn.tree import DecisionTreeClassifier

    >>> clf = DecisionTreeClassifier(random_state=0)
    >>> iris = load_iris()

    >>> cross_val_score(clf, iris.data, iris.target, cv=10)
    ...                             # doctest: +SKIP
    ...
    array([ 1.     ,  0.93...,  0.86...,  0.93...,  0.93...,
            0.93...,  0.93...,  1.     ,  0.93...,  1.      ])
    """
    def __init__(self, criterion="gini",
                       max_depth=10,
                       min_split=1,
                       min_density=0.1,
                       max_features=None,
                       random_state=None):
    def predict_proba(self, X):
        """Predict class probabilities of the input samples X.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        P : array of shape = [n_samples, n_classes]
            The class probabilities of the input samples. Classes are ordered
            by arithmetical order.
        """
        X = array2d(X, dtype=DTYPE)

        n_samples, n_features = X.shape
        P = self.tree.predict(X)
        if self.tree is None:
            raise Exception("Tree not initialized. Perform a fit first.")


        if self.n_features != n_features:
            raise ValueError("Number of features of the model must "
                             " match the input. Model n_features is %s and "
                             " input n_features is %s "
                             % (self.n_features, n_features))

        P /= P.sum(axis=1)[:, np.newaxis]
        return P
    def predict_log_proba(self, X):
        """Predict class log-probabilities of the input samples X.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        P : array of shape = [n_samples, n_classes]
            The class log-probabilities of the input samples. Classes are
            ordered by arithmetical order.
        """
        return np.log(self.predict_proba(X))


class DecisionTreeRegressor(BaseDecisionTree, RegressorMixin):
    """A tree regressor.

    Parameters
    ----------
    criterion : string, optional (default="mse")
        The function to measure the quality of a split. The only supported
        criterion is "mse" for the mean squared error.

    max_depth : integer or None, optional (default=10)
        The maximum depth of the tree. If None, then nodes are expanded until
        all leaves are pure or until all leaves contain less than min_split
        samples.

    min_split : integer, optional (default=1)
        The minimum number of samples required to split an internal node.

    min_density : float, optional (default=0.1)
        The minimum density of the `sample_mask` (i.e. the fraction of samples
        in the mask). If the density falls below this threshold the mask is
        recomputed and the input data is packed which results in data copying.
        If `min_density` equals to one, the partitions are always represented
        as copies of the original data. Otherwise, partitions are represented
        as bit masks (aka sample masks).

    max_features : int or None, optional (default=None)
        The number of features to consider when looking for the best split.
        If None, all features are considered, otherwise max_features are chosen
        at random.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Decision_tree_learning

    .. [2] L. Breiman, J. Friedman, R. Olshen, and C. Stone, "Classification
           and Regression Trees", Wadsworth, Belmont, CA, 1984.

    .. [3] T. Hastie, R. Tibshirani and J. Friedman. "Elements of Statistical
           Learning", Springer, 2009.

    See also
    --------
    DecisionTreeClassifier

    Examples
    --------
    >>> from sklearn.datasets import load_boston
    >>> from sklearn.cross_validation import cross_val_score
    >>> from sklearn.tree import DecisionTreeRegressor

    >>> boston = load_boston()
    >>> regressor = DecisionTreeRegressor(random_state=0)

    R2 scores (a.k.a. coefficient of determination) over 10-folds CV:

    >>> cross_val_score(regressor, boston.data, boston.target, cv=10)
    ...                    # doctest: +SKIP
    ...
    array([ 0.61..., 0.57..., -0.34..., 0.41..., 0.75...,
            0.07..., 0.29..., 0.33..., -1.42..., -1.77...])
    """
    def __init__(self, criterion="mse",
                       max_depth=10,
                       min_split=1,
                       min_density=0.1,
                       max_features=None,
                       random_state=None):

