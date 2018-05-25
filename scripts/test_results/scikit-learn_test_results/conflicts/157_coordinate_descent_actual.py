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
        self.coef_ = w0
        self.coef_ = w0
    def fit(self, X, Y, maxit=100, tol=1e-4):
        """Fit Lasso model with coordinate descent"""
        X = np.asanyarray(X, dtype=np.float64)
        Y = np.asanyarray(Y, dtype=np.float64)
        nsamples = X.shape[0]
        alpha = self.alpha * nsamples
        if self.coef_ is None:
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
            self.coef_ = np.zeros(X.shape[1], dtype=np.float64)
        self.coef_, self.dual_gap_, self.eps_ = \
                    lasso_coordinate_descent(self.coef_, alpha, X, Y, maxit, 10, tol)
        if self.dual_gap_ > self.eps_:
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
            warnings.warn('Objective did not converge, you might want to increase the number of interations')
        # return self for chaining fit and predict calls
        return self
    def predict(self, X):
        """Linear model prediction: compute the dot product with the weights"""
        X = np.asanyarray(X)
        return np.dot(X, self.coef_)
    def compute_density(self):
        """Ratio of non-zero weights in the model"""
        return density(self.coef_)












class Lasso(LinearModel):
    def __init__(self, alpha=1.0, w0=None):
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)
        super(Lasso, self).__init__(w0)
        self.alpha = float(alpha)
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
=======
def __init__(self, alpha=1.0, rho=0.5, w0=None, tol=1e-4):
>>>>>>> LOCAL
<<<<<<< REMOTE
def fit(self, X, Y, maxit=100, tol=1e-4):
=======
def fit(self, X, Y, maxit=100):
>>>>>>> LOCAL
    def __repr__(self):
        return "ElasticNet cd"











