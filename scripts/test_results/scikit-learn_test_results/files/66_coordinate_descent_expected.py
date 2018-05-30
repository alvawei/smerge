# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
#         Fabian Pedregosa <fabian.pedregosa@inria.fr>
#         Olivier Grisel <olivier.grisel@ensta.org>
#
# License: BSD Style.

import warnings
import numpy as np

from .base import LinearModel
from ..utils import as_float_array
from ..cross_val import check_cv
from . import cd_fast


###############################################################################
# ElasticNet model

class ElasticNet(LinearModel):
    """Linear Model trained with L1 and L2 prior as regularizer

    rho=1 is the lasso penalty. Currently, rho <= 0.01 is not
    reliable, unless you supply your own sequence of alpha.

    Parameters
    ----------
    alpha : float
        Constant that multiplies the penalty terms. Defaults to 1.0
        See the notes for the exact mathematical meaning of this
        parameter

    rho : float
        The ElasticNet mixing parameter, with 0 < rho <= 1. For rho = 0
        the penalty is an L1 penalty. For rho = 1 it is an L2 penalty.
        For 0 < rho < 1, the penalty is a combination of L1 and L2

    fit_intercept: bool
        Whether the intercept should be estimated or not. If False, the
        data is assumed to be already centered.

    normalize : boolean, optional
        If True, the regressors X are normalized

    precompute : True | False | 'auto' | array-like
        Whether to use a precomputed Gram matrix to speed up
        calculations. If set to 'auto' let us decide. The Gram
        matrix can also be passed as argument.

    max_iter: int, optional
        The maximum number of iterations

    overwrite_X : boolean, optionnal
        If True, X will not be copied
        Default is False

    tol: float, optional
        The tolerance for the optimization: if the updates are
        smaller than 'tol', the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than tol.

    Notes
    -----
    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a fortran contiguous numpy array.

    The parameter rho corresponds to alpha in the glmnet R package
    while alpha corresponds to the lambda parameter in glmnet.
    More specifically, the penalty is::

        alpha*rho*L1 + alpha*(1-rho)*L2

    If you are interested in controlling the L1 and L2 penalty
    separately, keep in mind that this is equivalent to::

        a*L1 + b*L2

    for::

        alpha = a + b and rho = a/(a+b)

    """

    def __init__(self, alpha=1.0, rho=0.5, fit_intercept=True,
                 normalize=False, precompute='auto', max_iter=1000,
                 overwrite_X=False, tol=1e-4):
        self.alpha = alpha
        self.rho = rho
        self.coef_ = None
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.precompute = precompute
        self.max_iter = max_iter
        self.overwrite_X = overwrite_X
        self.tol = tol

    def fit(self, X, y, Xy=None, coef_init=None):
        """Fit Elastic Net model with coordinate descent

        Parameters
        -----------
        X: ndarray, (n_samples, n_features)
            Data
        y: ndarray, (n_samples)
            Target
        Xy : array-like, optional
            Xy = np.dot(X.T, y) that can be precomputed. It is useful
            only when the Gram matrix is precomuted.
        coef_init: ndarray of shape n_features
            The initial coeffients to warm-start the optimization

        Notes
        -----

        Coordinate descent is an algorithm that considers each column of
        data at a time hence it will automatically convert the X input
        as a fortran contiguous numpy array if necessary.

        To avoid memory re-allocation it is advised to allocate the
        initial data in memory directly using that format.
        """
        X = np.asanyarray(X, dtype=np.float64)
        y = np.asanyarray(y, dtype=np.float64)
        X = as_float_array(X, self.overwrite_X)

        X, y, X_mean, y_mean, X_std = self._center_data(X, y, self.fit_intercept,
                self.normalize)

        if coef_init is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        else:
            self.coef_ = coef_init

        n_samples = X.shape[0]
        alpha = self.alpha * self.rho * n_samples
        beta = self.alpha * (1.0 - self.rho) * n_samples

        X = np.asfortranarray(X)  # make data contiguous in memory

        # precompute if n_samples > n_features
        if hasattr(self.precompute, '__array__'):
            Gram = self.precompute
        elif self.precompute == True or \
               (self.precompute == 'auto' and X.shape[0] > X.shape[1]):
            Gram = np.dot(X.T, X)
        else:
            Gram = None

        if Gram is None:
            self.coef_, self.dual_gap_, self.eps_ = \
                    cd_fast.enet_coordinate_descent(self.coef_, alpha, beta,
                                                    X, y, self.max_iter,
                                                    self.tol)
        else:
            if Xy is None:
                Xy = np.dot(X.T, y)
            self.coef_, self.dual_gap_, self.eps_ = \
                    cd_fast.enet_coordinate_descent_gram(self.coef_, alpha,
                                beta, Gram, Xy, y, self.max_iter, self.tol)

        self._set_intercept(X_mean, y_mean, X_std)

        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want'
                          ' to increase the number of iterations')

        # return self for chaining fit and predict calls
        return self


###############################################################################
# Lasso model

class Lasso(ElasticNet):
    """Linear Model trained with L1 prior as regularizer (aka the Lasso)

    Technically the Lasso model is optimizing the same objective function as
    the Elastic Net with rho=1.0 (no L2 penalty).

    Parameters
    ----------
    alpha : float, optional
        Constant that multiplies the L1 term. Defaults to 1.0

    fit_intercept : boolean
        whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).

    normalize : boolean, optional
        If True, the regressors X are normalized

    overwrite_X : boolean, optionnal
        If True, X will not be copied
        Default is False

    precompute : True | False | 'auto' | array-like
        Whether to use a precomputed Gram matrix to speed up
        calculations. If set to 'auto' let us decide. The Gram
        matrix can also be passed as argument.

    max_iter: int, optional
        The maximum number of iterations

    tol: float, optional
        The tolerance for the optimization: if the updates are
        smaller than 'tol', the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than tol.


    Attributes
    ----------
    `coef_` : array, shape = [n_features]
        parameter vector (w in the fomulation formula)

    `intercept_` : float
        independent term in decision function.

    Examples
    --------
    >>> from scikits.learn import linear_model
    >>> clf = linear_model.Lasso(alpha=0.1)
    >>> clf.fit([[0,0], [1, 1], [2, 2]], [0, 1, 2])
    Lasso(normalize=False, fit_intercept=True, max_iter=1000, precompute='auto',
       tol=0.0001, alpha=0.1, overwrite_X=False)
    >>> print clf.coef_
    [ 0.85  0.  ]
    >>> print clf.intercept_
    0.15

    See also
    --------
    LassoLars

    Notes
    -----
    The algorithm used to fit the model is coordinate descent.

    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a fortran contiguous numpy array.
    """

    def __init__(self, alpha=1.0, fit_intercept=True, normalize=False,
                 precompute='auto', overwrite_X=False, max_iter=1000, tol=1e-4):
        super(Lasso, self).__init__(alpha=alpha, rho=1.0,
                            fit_intercept=fit_intercept, precompute=precompute,
                            max_iter=max_iter, overwrite_X=overwrite_X, tol=tol)


###############################################################################
# Classes to store linear models along a regularization path

def lasso_path(X, y, eps=1e-3, n_alphas=100, alphas=None, fit_intercept=True,
               normalize=False, overwrite_X=False, verbose=False, **fit_params):
    """Compute Lasso path with coordinate descent

    Parameters
    ----------
    X : numpy array of shape [n_samples,n_features]
        Training data. Pass directly as fortran contiguous data to avoid
        unnecessary memory duplication

    y : numpy array of shape [n_samples]
        Target values

    eps : float, optional
        Length of the path. eps=1e-3 means that
        alpha_min / alpha_max = 1e-3

    n_alphas : int, optional
        Number of alphas along the regularization path

    alphas : numpy array, optional
        List of alphas where to compute the models.
        If None alphas are set automatically

    fit_params : kwargs
        keyword arguments passed to the Lasso fit method

    normalize : boolean, optional
        If True, the regressors X are normalized

    overwrite_X : boolean, optionnal
        If True, X will not be copied
        Default is False

    Returns
    -------
    models : a list of models along the regularization path

    Notes
    -----
    See examples/plot_lasso_coordinate_descent_path.py for an example.

    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a fortran contiguous numpy array.
    """
    return enet_path(X, y, rho=1., eps=eps, n_alphas=n_alphas, alphas=alphas,
                  fit_intercept=fit_intercept, normalize=normalize,
                  verbose=verbose, overwrite_X=overwrite_X, **fit_params)


def enet_path(X, y, rho=0.5, eps=1e-3, n_alphas=100, alphas=None,
              fit_intercept=True, normalize=False, verbose=False,
              overwrite_X=False, **fit_params):
    """Compute Elastic-Net path with coordinate descent

    Parameters
    ----------
    X : numpy array of shape [n_samples, n_features]
        Training data. Pass directly as fortran contiguous data to avoid
        unnecessary memory duplication

    y : numpy array of shape [n_samples]
        Target values

    rho : float, optional
        float between 0 and 1 passed to ElasticNet (scaling between
        l1 and l2 penalties). rho=1 corresponds to the Lasso

    eps : float
        Length of the path. eps=1e-3 means that
        alpha_min / alpha_max = 1e-3

    n_alphas : int, optional
        Number of alphas along the regularization path

    alphas : numpy array, optional
        List of alphas where to compute the models.
        If None alphas are set automatically

    fit_params : kwargs
        keyword arguments passed to the Lasso fit method

    normalize : boolean, optional
        If True, the regressors X are normalized

    overwrite_X : boolean, optionnal
        If True, X will not be copied
        Default is False

    Returns
    -------
    models : a list of models along the regularization path

    Notes
    -----
    See examples/plot_lasso_coordinate_descent_path.py for an example.
    """
    X = as_float_array(X, overwrite_X)
    X, y, X_mean, y_mean, X_std = LinearModel._center_data(X, y,
            fit_intercept, normalize)
    X = np.asfortranarray(X)  # make data contiguous in memory

    n_samples = X.shape[0]
    if alphas is None:
        alpha_max = np.abs(np.dot(X.T, y)).max() / (n_samples * rho)
        alphas = np.logspace(np.log10(alpha_max * eps), np.log10(alpha_max),
                             num=n_alphas)[::-1]
    else:
        alphas = np.sort(alphas)[::-1]  # make sure alphas are properly ordered
    coef_ = None  # init coef_
    models = []
    Xy = None

    if not 'precompute' in fit_params \
        or fit_params['precompute'] is True \
        or (fit_intercept and hasattr(fit_params['precompute'], '__array__')):
        fit_params['precompute'] = np.dot(X.T, X)
        if not 'Xy' in fit_params or fit_params['Xy'] is None:
            Xy = np.dot(X.T, y)

    for alpha in alphas:
        model = ElasticNet(alpha=alpha, rho=rho, fit_intercept=False)
        model.set_params(**fit_params)
        model.fit(X, y, coef_init=coef_, Xy=Xy)
        if fit_intercept:
            model.fit_intercept = True
            model._set_intercept(X_mean, y_mean, X_std)
        if verbose:
            print model
        coef_ = model.coef_.copy()
        models.append(model)
    return models


class LinearModelCV(LinearModel):
    """Base class for iterative model fitting along a regularization path"""

    def __init__(self, eps=1e-3, n_alphas=100, alphas=None, fit_intercept=True,
            normalize=False, precompute='auto', max_iter=1000, tol=1e-4,
            overwrite_X=False, cv=None):
        self.eps = eps
        self.n_alphas = n_alphas
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.precompute = precompute
        self.max_iter = max_iter
        self.tol = tol
        self.overwrite_X = overwrite_X
        self.cv = cv

    def fit(self, X, y):
        """Fit linear model with coordinate descent along decreasing alphas
        using cross-validation

        Parameters
        ----------

        X : numpy array of shape [n_samples,n_features]
            Training data. Pass directly as fortran contiguous data to avoid
            unnecessary memory duplication

        y : numpy array of shape [n_samples]
            Target values

        fit_params : kwargs
            keyword arguments passed to the Lasso fit method

        """
        X = np.asfortranarray(X, dtype=np.float64)
        y = np.asanyarray(y, dtype=np.float64)

        # All LinearModelCV parameters except 'cv' are acceptable
        path_params = self._get_params()
        del path_params['cv']

        # Start to compute path on full data
        models = self.path(X, y, **path_params)

        # Update the alphas list
        alphas = [model.alpha for model in models]
        n_alphas = len(alphas)
        path_params.update({'alphas': alphas, 'n_alphas': n_alphas})

        # init cross-validation generator
        cv = check_cv(self.cv, X)

        # Compute path for all folds and compute MSE to get the best alpha
        folds = list(cv)
        mse_alphas = np.zeros((len(folds), n_alphas))
        for i, (train, test) in enumerate(folds):
            models_train = self.path(X[train], y[train], **path_params)
            for i_alpha, model in enumerate(models_train):
                y_ = model.predict(X[test])
                mse_alphas[i, i_alpha] += ((y_ - y[test]) ** 2).mean()

        i_best_alpha = np.argmin(np.mean(mse_alphas, axis=0))
        model = models[i_best_alpha]

        self.coef_ = model.coef_
        self.intercept_ = model.intercept_
        self.alpha = model.alpha
        self.alphas = np.asarray(alphas)
        self.coef_path_ = np.asarray([model.coef_ for model in models])
        self.mse_path_ = mse_alphas.T
        return self


class LassoCV(LinearModelCV):
    """Lasso linear model with iterative fitting along a regularization path

    The best model is selected by cross-validation.

    Parameters
    ----------
    eps : float, optional
        Length of the path. eps=1e-3 means that
        alpha_min / alpha_max = 1e-3.

    n_alphas : int, optional
        Number of alphas along the regularization path

    alphas : numpy array, optional
        List of alphas where to compute the models.
        If None alphas are set automatically

    precompute : True | False | 'auto' | array-like
        Whether to use a precomputed Gram matrix to speed up
        calculations. If set to 'auto' let us decide. The Gram
        matrix can also be passed as argument.

    max_iter: int, optional
        The maximum number of iterations

    tol: float, optional
        The tolerance for the optimization: if the updates are
        smaller than 'tol', the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than tol.

    cv : integer or crossvalidation generator, optional
        If an integer is passed, it is the number of fold (default 3).
        Specific crossvalidation objects can be passed, see
        scikits.learn.cross_val module for the list of possible objects

    Notes
    -----
    See examples/linear_model/lasso_path_with_crossvalidation.py
    for an example.

    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a fortran contiguous numpy array.
    """

    path = staticmethod(lasso_path)
    estimator = Lasso


class ElasticNetCV(LinearModelCV):
    """Elastic Net model with iterative fitting along a regularization path

    The best model is selected by cross-validation.

    Parameters
    ----------
    rho : float, optional
        float between 0 and 1 passed to ElasticNet (scaling between
        l1 and l2 penalties). For rho = 0
        the penalty is an L1 penalty. For rho = 1 it is an L2 penalty.
        For 0 < rho < 1, the penalty is a combination of L1 and L2

    eps : float, optional
        Length of the path. eps=1e-3 means that
        alpha_min / alpha_max = 1e-3.

    n_alphas : int, optional
        Number of alphas along the regularization path

    alphas : numpy array, optional
        List of alphas where to compute the models.
        If None alphas are set automatically

    precompute : True | False | 'auto' | array-like
        Whether to use a precomputed Gram matrix to speed up
        calculations. If set to 'auto' let us decide. The Gram
        matrix can also be passed as argument.

    max_iter: int, optional
        The maximum number of iterations

    tol: float, optional
        The tolerance for the optimization: if the updates are
        smaller than 'tol', the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than tol.

    cv : integer or crossvalidation generator, optional
        If an integer is passed, it is the number of fold (default 3).
        Specific crossvalidation objects can be passed, see 
        scikits.learn.cross_val module for the list of possible objects


    Notes
    -----
    See examples/linear_model/lasso_path_with_crossvalidation.py
    for an example.

    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a fortran contiguous numpy array.

    The parameter rho corresponds to alpha in the glmnet R package
    while alpha corresponds to the lambda parameter in glmnet.
    More specifically, the penalty is::

        alpha*rho*L1 + alpha*(1-rho)*L2

    If you are interested in controlling the L1 and L2 penalty
    separately, keep in mind that this is equivalent to::

        a*L1 + b*L2

    for::

        alpha = a + b and rho = a/(a+b)

    """

    path = staticmethod(enet_path)
    estimator = ElasticNet

    def __init__(self, rho=0.5, eps=1e-3, n_alphas=100, alphas=None,
                 fit_intercept=True, normalize=False, precompute='auto',
                 max_iter=1000, tol=1e-4, cv=None, overwrite_X=False):
        self.rho = rho
        self.eps = eps
        self.n_alphas = n_alphas
        self.alphas = alphas
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.precompute = precompute
        self.max_iter = max_iter
        self.tol = tol
        self.cv = cv
        self.overwrite_X = overwrite_X
