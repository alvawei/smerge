# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD Style.

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


class LinearModel(object):
    """Base class for Linear Model optimized with coordinate descent"""
    def __init__(self, w0=None):
        # weights of the model (can be lazily initialized by the ``fit`` method)
        self.coef_ = w0
        # weights of the model (can be lazily initialized by the ``fit`` method)
        self.coef_ = w0
    def predict(self, X):
        """Linear model prediction: compute the dot product with the weights"""
        X = np.asanyarray(X)
    def compute_density(self):
        """Ratio of non-zero weights in the model"""
        return density(self.coef_)












class Lasso(LinearModel):
    """
<<<<<<< REMOTE
Linear Model trained with L1 prior as regularizer (a.k.a. the
    lasso).
=======
def __init__(self, alpha=1.0, w0=None):
>>>>>>> LOCAL
<<<<<<< REMOTE
The lasso estimate solves the minization of the least-squares
=======
def fit(self, X, y, maxit=100, tol=1e-4):
>>>>>>> LOCAL
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
    def __init__(self, alpha=1.0, w0=None, tol=1e-4):
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)
        self.tol = tol
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)
        self.tol = tol
    def fit(self, X, Y, maxit=100):
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * nsamples
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        self.coef_, self.dual_gap_, self.eps_ = \
                    lasso_coordinate_descent(self.coef_, alpha, X, Y, maxit, 10, self.tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        """Fit Lasso model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * nsamples
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        self.coef_, self.dual_gap_, self.eps_ = \
                    lasso_coordinate_descent(self.coef_, alpha, X, Y, maxit, 10, self.tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self
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
def __init__(self, alpha=1.0, rho=0.5, w0=None, tol=1e-4):
=======
def __init__(self, alpha=1.0, rho=0.5, w0=None):
>>>>>>> LOCAL
<<<<<<< REMOTE
def fit(self, X, Y, maxit=100):
=======
def fit(self, X, Y, maxit=100, tol=1e-4):
>>>>>>> LOCAL
    def __repr__(self):
        return "ElasticNet cd"











