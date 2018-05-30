# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD Style.

# $Id$
"""Implementation of regularized linear regression with Coordinate Descent

This implementation is focused on regularizers that lead to sparse parameters
(many zeros) such as the laplacian (L1) and Elastic Net (L1 + L2) priors:

  http://en.wikipedia.org/wiki/Generalized_linear_model

The objective function to minimize is for the Lasso::

        0.5 * ||R||_2 ^ 2 + alpha * ||w||_1

and for the Elastic Network::

        0.5 * ||R||_2 ^ 2 + alpha * ||w||_1 + beta * 0.5 * ||w||_2 ^ 2

Where R are the residuals between the output of the model and the expected
value and w is the vector of weights to fit.
"""

import numpy as np
import scipy.linalg as linalg
from lasso_cd import lasso_coordinate_descent as lasso_coordinate_descent_slow
from enet_cd import enet_coordinate_descent as enet_coordinate_descent_slow
from iteration_callbacks import IterationCallbackMaxit, IterationCallbackFunc
from utils import enet_dual_gap, lasso_dual_gap, lasso_objective, \
                  enet_objective, density

# Attempt to improve speed with cython
try:
    from lasso_cd_fast import lasso_coordinate_descent \
            as lasso_coordinate_descent_fast
    from enet_cd_fast import enet_coordinate_descent \
            as enet_coordinate_descent_fast
    lasso_coordinate_descent = lasso_coordinate_descent_fast
    enet_coordinate_descent = enet_coordinate_descent_fast
except ImportError:
    lasso_coordinate_descent = lasso_coordinate_descent_slow
    enet_coordinate_descent = enet_coordinate_descent_slow
    print "Using Python version of coordinate descent"

class LinearModel(object):
    """Base class for Linear Model optimized with coordinate descent"""
    def __init__(self, w0=None, callbacks=None):
        # weights of the model (can be lazily initialized by the ``fit`` method)
        self.w = w0
        # callbacks that handles recording of the historic data
        # and can stop iterations
        self.callbacks = []
        if callbacks is not None:
            for callback in callbacks:
                self.callbacks.append(callback)
        self.learner = None
        self.dual_gap_func = None
    def fit(self, X, Y, maxit=100, tol=1e-4):
        """Fit Lasso model with coordinate descent"""
        X, y = np.asanyarray(X), np.asanyarray(y)
        n_samples, n_features = X.shape
        if tol is not None:
            cb_dual_gap = IterationCallbackFunc(self._dual_gap_func, tol=tol)
            self.callbacks.append(cb_dual_gap)
        if self.w is None:
            self.w = np.zeros(n_features)
        self.w = self.learner(self, X, y, maxit)
        # return self for chaining fit and predict calls
        return self
    def compute_density(self):
    def predict(self, X):
        """Linear model prediction: compute the dot product with the weights"""
        X = np.asanyarray(X)
        return np.dot(X, self.coef_)
    def compute_density(self):
        """Ratio of non-zero weights in the model"""
        return density(self.coef_)
    @property
    def coef_(self):
        return self












class Lasso(LinearModel):
    """
    Linear Model trained with L1 prior as regularizer (a.k.a. the
    lasso).

    The lasso estimate solves the minization of the least-squares
    penalty with alpha * ||beta||_1 added, where alpha is a constant and
    ||beta||_1 is the L1-norm of the parameter vector.

    This formulation is useful in some context due to its tendency to
    prefer solutions with fewer parameter values, effectively reducing
    the number of variables upon which the given solution is
    dependent. For this reason, the LASSO and its variants are
    fundamental to the field of compressed sensing.

    Parameters
    ----------
    alpha : double
        Constant that multiplies the L1 term.

    Attributes
    ----------
    `coef_` : array, shape = [nfeatures]
        parameter vector (w in the fomulation formula)

    Examples
    --------
    >>> from scikits.learn import glm
    >>> clf = glm.Lasso()
    >>> clf.fit([[0,0], [1, 1], [2, 2]], [0, 1, 2])
    Lasso Coordinate Descent
    >>> print clf.coef_
    [ 0.4  0. ]

    Notes
    -----
    The algorithm used to fit the model is coordinate descent.x
    """
<<<<<<< REMOTE
    def __init__(self, alpha=1.0, w0=None):
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)

=======
    def __init__(self, alpha=1.0, w0=None, tol=1e-4):
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)
        self.tol = tol

>>>>>>> LOCAL
<<<<<<< REMOTE
    def fit(self, X, Y, maxit=100, tol=1e-4):
        """Fit Lasso model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * nsamples
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        self.coef_, self.dual_gap_, self.eps_ = \
                    lasso_coordinate_descent(self.coef_, alpha, X, Y, maxit, 10, tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self

=======
    def fit(self, X, Y, maxit=100):
        """Fit Lasso model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * nsamples
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        self.coef_, self.dual_gap_, self.eps_ = \
                    lasso_coordinate_descent(self.coef_, alpha, X, Y, maxit, 10, self.tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self

>>>>>>> LOCAL
    def __repr__(self):
        return "Lasso Coordinate Descent"





class ElasticNet(LinearModel):
    """Linear Model trained with L1 and L2 prior as regularizer

    rho=1 is the lasso penalty. Currently, rho <= 0.01 is not
    reliable, unless you supply your own sequence of alpha.

    Parameters
    ----------
    alpha : double
        TODO
    rho : double
        The ElasticNet mixing parameter, with 0 < rho <= 1. 
    """
<<<<<<< REMOTE
    def __init__(self, alpha=1.0, rho=0.5, w0=None):
        super(ElasticNet, self).__init__(w0)
        self.alpha = alpha
        self.rho = rho

=======
    def __init__(self, alpha=1.0, rho=0.5, w0=None, tol=1e-4):
        super(ElasticNet, self).__init__(w0)
        self.alpha = alpha
        self.rho = rho
        self.tol = tol

>>>>>>> LOCAL
<<<<<<< REMOTE
    def fit(self, X, Y, maxit=100, tol=1e-4):
        """Fit Elastic Net model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * self.rho * nsamples
        beta = self.alpha * (1.0 - self.rho) * nsamples
        self.coef_, self.dual_gap_, self.eps_ = \
                    enet_coordinate_descent(self.coef_, alpha, beta, X, Y, maxit, 10, tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self

=======
    def fit(self, X, Y, maxit=100):
        """Fit Elastic Net model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * self.rho * nsamples
        beta = self.alpha * (1.0 - self.rho) * nsamples
        self.coef_, self.dual_gap_, self.eps_ = \
                enet_coordinate_descent(self.coef_, alpha, beta, X, Y,
                                        maxit, 10, self.tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self

>>>>>>> LOCAL
    def __repr__(self):
        return "ElasticNet cd"





def lasso_path(X, y, factor=0.95, n_alphas = 10, **kwargs):
    """Compute Lasso path with coordinate descent"""
    alpha_max = np.abs(np.dot(X.T, y)).max()
    alpha = alpha_max
    model = Lasso(alpha=alpha_max)
    weights = []
    alphas = []
    for _ in range(n_alphas):
        model.alpha *= factor
        model.fit(X, y, **kwargs)
        alphas.append(model.alpha)
        weights.append(model.coef_.copy())
    alphas = np.asarray(alphas)
    weights = np.asarray(weights)
    return alphas, weights



def enet_path(X, y, factor=0.95, n_alphas=10, beta=1.0, **kwargs):
    """Compute Elastic-Net path with coordinate descent"""
    alpha_max = np.abs(np.dot(X.T, y)).max()
    alpha = alpha_max
    model = ElasticNet(alpha=alpha, beta=beta)
    weights = []
    alphas = []
    for _ in range(n_alphas):
        model.alpha *= factor
        model.fit(X, y, **kwargs)
        alphas.append(model.alpha)
        weights.append(model.coef_.copy())
    alphas = np.asarray(alphas)
    weights = np.asarray(weights)
    return alphas, weights



