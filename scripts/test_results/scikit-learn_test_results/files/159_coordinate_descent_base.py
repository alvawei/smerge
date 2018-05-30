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

    def fit(self, X, y, maxit=100, tol=1e-4):
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

    def predict(self, X):
        """Linear model prediction: compute the dot product with the weights"""
        X = np.asanyarray(X)
        y = np.dot(X, self.w)
        return y

    def compute_density(self):
        """Ratio of non-zero weights in the model"""
        return density(self.w)

    @property
    def coef_(self):
        return self.w

class Lasso(LinearModel):
    """Linear Model trained with L1 prior as regularizer (a.k.a. the Lasso)"""

    def __init__(self, alpha=1.0, w0=None, callbacks=None):
        super(Lasso, self).__init__(w0, callbacks)
        self.alpha = alpha
        self.learner = lasso_coordinate_descent

    def _dual_gap_func(self, X, y, w, **kw):
        return lasso_dual_gap(X, y, w, kw['alpha'])[0]

    def __repr__(self):
        return "Lasso cd"


class ElasticNet(LinearModel):
    """Linear Model trained with L1 and L2 prior as regularizer"""

    def __init__(self, alpha=1.0, beta=1.0, w0=None, callbacks=None):
        super(ElasticNet, self).__init__(w0, callbacks)
        self.alpha = alpha
        self.beta = beta
        self.learner = enet_coordinate_descent

    def _dual_gap_func(self, X, y, w, **kw):
        return enet_dual_gap(X, y, w, kw['alpha'], kw['beta'])[0]

    def __repr__(self):
        return "ElasticNet cd"


def lasso_path(X, y, factor=0.95, n_alphas = 10, **kwargs):
    """Compute Lasso path with coordinate descent"""
    alpha_max = np.abs(np.dot(X.T, y)).max()
    alpha = alpha_max
    model = Lasso(alpha=alpha)
    weights = []
    alphas = []
    for _ in range(n_alphas):
        model.alpha *= factor
        model.fit(X, y, **kwargs)

        alphas.append(model.alpha)
        weights.append(model.w.copy())

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
        weights.append(model.w.copy())

    alphas = np.asarray(alphas)
    weights = np.asarray(weights)
    return alphas, weights
