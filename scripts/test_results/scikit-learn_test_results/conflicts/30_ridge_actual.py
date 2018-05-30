"""
Ridge regression
"""

# Author:   Mathieu Blondel <mathieu@mblondel.org>
#           Reuben Fletcher-Costin <reuben.fletchercostin@gmail.com>
# License: Simplified BSD

import warnings
import warnings
import numpy as np


from .base import LinearModel
from ..utils.extmath import safe_sparse_dot
from ..utils import safe_asarray

from ..preprocessing import LabelBinarizer
from ..grid_search import GridSearchCV


def _solve(A, b, solver, tol):
    # helper method for ridge_regression, A is symmetric positive

    if solver == 'auto':
        if hasattr(A, 'todense'):
            solver = 'sparse_cg'
        else:
            solver = 'dense_cholesky'

    if solver == 'sparse_cg':
        if b.ndim < 2:
            from scipy.sparse import linalg as sp_linalg
            sol, error = sp_linalg.cg(A, b, tol=tol)
            if error:
                raise ValueError("Failed with error code %d" % error)
            return sol
        else:
            # sparse_cg cannot handle a 2-d b.
            sol = []
            for j in range(b.shape[1]):
                sol.append(_solve(A, b[:, j], solver="sparse_cg", tol=tol))
            return np.array(sol).T

    elif solver == 'dense_cholesky':
        from scipy import linalg
        if hasattr(A, 'todense'):
            A = A.todense()
        return linalg.solve(A, b, sym_pos=True, overwrite_a=True)
    else:
        raise NotImplementedError('Solver %s not implemented' % solver)


def ridge_regression(X, y, alpha, sample_weight=1.0, solver='auto', tol=1e-3):
    """Solve the ridge equation by the method of normal equations.

    Parameters
    ----------
    X : {array-like, sparse matrix}, shape = [n_samples, n_features]
        Training data

    y : array-like, shape = [n_samples] or [n_samples, n_responses]
        Target values

    sample_weight : float or numpy array of shape [n_samples]
        Individual weights for each sample

    solver : {'auto', 'dense_cholesky', 'sparse_cg'}, optional
        Solver to use in the computational routines. 'delse_cholesky'
        will use the standard scipy.linalg.solve function, 'sparse_cg'
        will use the a conjugate gradient solver as found in
        scipy.sparse.linalg.cg while 'auto' will chose the most
        appropiate depending on the matrix X.

    tol: float
        Precision of the solution.

    Returns
    -------
    coef: array, shape = [n_features] or [n_responses, n_features]
        Weight vector(s).

    Notes
    -----
    This function won't compute the intercept.
    """

    n_samples, n_features = X.shape
    is_sparse = False

    if hasattr(X, 'todense'):  # lazy import of scipy.sparse
        from scipy import sparse
        is_sparse = sparse.issparse(X)

    if is_sparse:
        if n_features > n_samples or \
           isinstance(sample_weight, np.ndarray) or \
           sample_weight != 1.0:
            I = sparse.lil_matrix((n_samples, n_samples))
            I.setdiag(np.ones(n_samples) * alpha * sample_weight)
            c = _solve(X * X.T + I, y, solver, tol)
            coef = X.T * c

        else:
            I = sparse.lil_matrix((n_features, n_features))
            I.setdiag(np.ones(n_features) * alpha)
            coef = _solve(X.T * X + I, X.T * y, solver, tol)
    else:
        if n_features > n_samples or \
           isinstance(sample_weight, np.ndarray) or \
           sample_weight != 1.0:
            # kernel ridge
            # w = X.T * inv(X X^t + alpha*Id) y
            A = np.dot(X, X.T)
            A.flat[::n_samples + 1] += alpha * sample_weight
            coef = np.dot(X.T, _solve(A, y, solver, tol))

        else:
            # ridge
            # w = inv(X^t X + alpha*Id) * X.T y
            A = np.dot(X.T, X)
            A.flat[::n_features + 1] += alpha
            coef = _solve(A, np.dot(X.T, y), solver, tol)

    return coef.T


class Ridge(LinearModel):
    """Linear least squares with l2 regularization.

    This model solves a regression model where the loss function is
    the linear least squares function and regularization is given by
    the l2-norm. Also known as Ridge Regression or Tikhonov regularization.
    This estimator has built-in support for multi-variate regression
    (i.e., when y is a 2d-array of shape [n_samples, n_responses]).

    Parameters
    ----------
    alpha : float
        Small positive values of alpha improve the conditioning of the
        problem and reduce the variance of the estimates.
        Alpha corresponds to (2*C)^-1 in other linear models such as
        LogisticRegression or LinearSVC.

    fit_intercept : boolean
        Whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).

    normalize : boolean, optional
        If True, the regressors X are normalized

    copy_X : boolean, optional, default True
        If True, X will be copied; else, it may be overwritten.

    tol: float
        Precision of the solution.

    Attributes
    ----------

    `coef_` : array, shape = [n_features] or [n_responses, n_features]
        Weight vector(s).

    See also
    --------
    RidgeClassifier, RidgeCV

    Examples
    --------
    >>> from sklearn.linear_model import Ridge
    >>> import numpy as np
    >>> n_samples, n_features = 10, 5
    >>> np.random.seed(0)
    >>> y = np.random.randn(n_samples)
    >>> X = np.random.randn(n_samples, n_features)
    >>> clf = Ridge(alpha=1.0)
    >>> clf.fit(X, y) # doctest: +NORMALIZE_WHITESPACE
    Ridge(alpha=1.0, copy_X=True, fit_intercept=True, normalize=False,
       tol=0.001)
    """

    def __init__(self, alpha=1.0, fit_intercept=True, normalize=False,
            copy_X=True, tol=1e-3):
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X
        self.tol = tol

    def fit(self, X, y, sample_weight=1.0, solver='auto'):
        """Fit Ridge regression model

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training data

        y : array-like, shape = [n_samples] or [n_samples, n_responses]
            Target values

        sample_weight : float or numpy array of shape [n_samples]
            Individual weights for each sample

        solver : {'auto', 'dense_cholesky', 'sparse_cg'}
            Solver to use in the computational
            routines. 'delse_cholesky' will use the standard
            scipy.linalg.solve function, 'sparse_cg' will use the a
            conjugate gradient solver as found in
            scipy.sparse.linalg.cg while 'auto' will chose the most
            appropiate depending on the matrix X.

        Returns
        -------
        self : returns an instance of self.
        """
        X = safe_asarray(X, dtype=np.float)
        y = np.asarray(y, dtype=np.float)

        X, y, X_mean, y_mean, X_std = \
           self._center_data(X, y, self.fit_intercept,
                   self.normalize, self.copy_X)

        self.coef_ = ridge_regression(X, y, self.alpha, sample_weight,
                                      solver, self.tol)
        self._set_intercept(X_mean, y_mean, X_std)
        return self


class RidgeClassifier(Ridge):
    """Classifier using Ridge regression.

    Parameters
    ----------
    alpha : float
        Small positive values of alpha improve the conditioning of the
        problem and reduce the variance of the estimates.
        Alpha corresponds to (2*C)^-1 in other linear models such as
        LogisticRegression or LinearSVC.

    fit_intercept : boolean
        Whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).

    normalize : boolean, optional
        If True, the regressors X are normalized

    copy_X : boolean, optional, default True
        If True, X will be copied; else, it may be overwritten.

    tol: float
        Precision of the solution.

    class_weight : dict, optional
        Weights associated with classes in the form
        {class_label : weight}. If not given, all classes are
        supposed to have weight one.


    Attributes
    ----------

    `coef_` : array, shape = [n_features] or [n_classes, n_features]
        Weight vector(s).

    See also
    --------
    Ridge, RidgeClassifierCV

    Notes
    -----
    For multi-class classification, n_class classifiers are trained in
    a one-versus-all approach. Concretely, this is implemented by taking
    advantage of the multi-variate response support in Ridge.
    """
<<<<<<< REMOTE

=======
    def __init__(self, alpha=1.0, fit_intercept=True, normalize=False,
            copy_X=True, tol=1e-3, class_weight=None):
        super(RidgeClassifier, self).__init__(alpha=alpha,
                fit_intercept=fit_intercept, normalize=normalize,
                copy_X=copy_X, tol=tol)
        self.class_weight = class_weight


>>>>>>> LOCAL
    def fit(self, X, y, solver='auto'):
        """Fit Ridge regression model.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples,n_features]
            Training data

        y : array-like, shape = [n_samples]
            Target values

        solver : {'auto', 'dense_cholesky', 'sparse_cg'}
            Solver to use in the computational
            routines. 'delse_cholesky' will use the standard
            scipy.linalg.solve function, 'sparse_cg' will use the a
            conjugate gradient solver as found in
            scipy.sparse.linalg.cg while 'auto' will chose the most
            appropiate depending on the matrix X.

        Returns
        -------
        self : returns an instance of self.
        """
        if self.class_weight is None:
            self.class_weight = {}

        sample_weight_classes = np.array([self.class_weight.get(k, 1.0) for k in y])
<<<<<<< REMOTE

=======
Ridge.fit(self, X, Y, solver=solver, sample_weight=sample_weight_classes)
>>>>>>> LOCAL
        self.label_binarizer = LabelBinarizer()

        Y = self.label_binarizer.fit_transform(y)
        return self
    def decision_function(self, X):
        return Ridge.decision_function(self, X)

    def predict(self, X):
        """Predict target values according to the fitted model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]

        Returns
        -------
        y : array, shape = [n_samples]
        """
        Y = self.decision_function(X)
        return self.label_binarizer.inverse_transform(Y)

class RidgeCV(LinearModel):
    """Ridge regression with built-in cross-validation.

    By default, it performs Generalized Cross-Validation, which is a form of
    efficient Leave-One-Out cross-validation. Currently, only the n_features >
    n_samples case is handled efficiently.

    Parameters
    ----------
    alphas: numpy array of shape [n_alpha]
        Array of alpha values to try.
        Small positive values of alpha improve the conditioning of the
        problem and reduce the variance of the estimates.
        Alpha corresponds to (2*C)^-1 in other linear models such as
        LogisticRegression or LinearSVC.

    fit_intercept : boolean
        Whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).

    normalize : boolean, optional
        If True, the regressors X are normalized

    score_func: callable, optional
        function that takes 2 arguments and compares them in
        order to evaluate the performance of prediciton (big is good)
        if None is passed, the score of the estimator is maximized

    loss_func: callable, optional
        function that takes 2 arguments and compares them in
        order to evaluate the performance of prediciton (small is good)
        if None is passed, the score of the estimator is maximized

    cv : cross-validation generator, optional
        If None, Generalized Cross-Validationn (efficient Leave-One-Out)
        will be used.


    Attributes
    ----------
    `coef_` : array, shape = [n_features] or [n_classes, n_features]
        Weight vector(s).

    See also
    --------
    Ridge: Ridge regression
    RidgeClassifier: Ridge classifiert
    RidgeCV: Ridge regression with built-in cross validation
    """

    <<<<<<< REMOTE
    def __init__(self, alphas=np.array([0.1, 1.0, 10.0]), fit_intercept=True,
                   normalize=False, score_func=None, loss_func=None, cv=None,
                   gcv_mode=None):
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.score_func = score_func
        self.loss_func = loss_func
        self.cv = cv
        self.gcv_mode = gcv_mode


=======
    def __init__(self, alphas=np.array([0.1, 1.0, 10.0]), fit_intercept=True,
                   normalize=False, score_func=None, loss_func=None, cv=None):
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.score_func = score_func
        self.loss_func = loss_func
        self.cv = cv
<<<<<<< REMOTE
self.gcv_mode = gcv_mode
=======

>>>>>>> LOCAL


=======
    def __init__(self, alphas=np.array([0.1, 1.0, 10.0]), fit_intercept=True,
            normalize=False, score_func=None, loss_func=None, cv=None):
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.score_func = score_func
        self.loss_func = loss_func
        self.cv = cv


>>>>>>> LOCAL
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.score_func = score_func
        self.loss_func = loss_func
        self.cv = cv
<<<<<<< REMOTE
self.gcv_mode = gcv_mode
=======

>>>>>>> LOCAL

    def fit(self, X, y, sample_weight=1.0):
        """Fit Ridge regression model

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training data

        y : array-like, shape = [n_samples] or [n_samples, n_responses]
            Target values

        sample_weight : float or array-like of shape [n_samples]
            Sample weight

        Returns
        -------
        self : Returns self.
        """
        if self.cv is None:
            estimator = _RidgeGCV(self.alphas, self.fit_intercept,
                                  self.score_func, self.loss_func,
                                  gcv_mode=self.gcv_mode)
            estimator.fit(X, y, sample_weight=sample_weight)
            self.best_alpha = estimator.best_alpha
        else:
            parameters = {'alpha': self.alphas}
            # FIXME: sample_weight must be split into training/validation data
            #        too!
            #fit_params = {'sample_weight' : sample_weight}
            fit_params = {}
            gs = GridSearchCV(Ridge(fit_intercept=self.fit_intercept),
                              parameters, fit_params=fit_params, cv=self.cv)
            gs.fit(X, y)
            estimator = gs.best_estimator_
            self.best_alpha = gs.best_estimator_.alpha

        self.coef_ = estimator.coef_
        self.intercept_ = estimator.intercept_

        return self
class RidgeClassifierCV(RidgeCV):
    def fit(self, X, y, sample_weight=1.0, class_weight=None):
        """Fit the ridge classifier.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.

        y : array-like, shape = [n_samples]
            Target values.

        sample_weight : float or numpy array of shape [n_samples]
            Sample weight

        class_weight : dict, optional
            Weights associated with classes in the form
            {class_label : weight}. If not given, all classes are
            supposed to have weight one.

        Returns
        -------
        self : object
            Returns self.
        """
        if class_weight != None:
            warnings.warn("'class_weight' is now an initialization parameter."
                    "Using it in the 'fit' method is deprecated.",
                    DeprecationWarning)
            self.class_weight = class_weight

        if self.class_weight is None:
            self.class_weight = {}

        sample_weight2 = np.array([self.class_weight.get(k, 1.0) for k in y])
        RidgeCV.fit(self, X, Y, sample_weight=sample_weight * sample_weight2)


        self.label_binarizer = LabelBinarizer()
        Y = self.label_binarizer.fit_transform(y)
        return self
    def decision_function(self, X):
        return RidgeCV.decision_function(self, X)

    def predict(self, X):
        """Predict target values according to the fitted model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]

        Returns
        -------
        y : array, shape = [n_samples]
        """
        Y = self.decision_function(X)
        return self.label_binarizer.inverse_transform(Y)

