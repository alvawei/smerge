
import numpy as np
from scipy import linalg

from .base import LinearModel

class Ridge(LinearModel):
    """
    Ridge regression.
    Parameters
    ----------
    alpha : float
        Small positive values of alpha improve the coditioning of the
        problem and reduce the variance of the estimates.
    fit_intercept : boolean
        wether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).
    Examples
    --------
    >>> import numpy as np
    >>> n_samples, n_features = 10, 5
    >>> np.random.seed(0)
    >>> Y = np.random.randn(n_samples)
    >>> X = np.random.randn(n_samples, n_features)
    >>> clf = Ridge(alpha=1.0)
    >>> clf.fit(X, Y)
    Ridge(alpha=1.0, fit_intercept=True)
    """
    def __init__(self, alpha=1.0, fit_intercept=True):
        self.alpha = alpha
    def fit(self, X, Y, **params):
        """
        Fit Ridge regression model
        Parameters
        ----------
        X : numpy array of shape [n_samples,n_features]
            Training data
        Y : numpy array of shape [n_samples]
            Target values
        Returns
        -------
        self : returns an instance of self.
        """
        self._set_params(**params)
        n_samples, n_features = X.shape
        X, Y = self._center_data (X, Y)
        else:
        if n_samples > n_features:
            # w = inv(X^t X + alpha*Id) * X.T y
            self.coef_ = linalg.solve(
                np.dot(X.T, X) + self.alpha * np.eye(n_features),
                np.dot(X.T, Y))
        self.intercept_ = self._ymean - np.dot(self._xmean, self.coef_)
        return self












class BayesianRidge(LinearModel):
    """
    simple bayesian framework (MAP).
    """
    def __init__(self, n_iter=300, th_w=1.e-12, compute_ll=False,
        fit_intercept=True):
        self.n_iter = n_iter
        self.compute_ll = compute_ll
        self.fit_intercept = fit_intercept
        self.n_iter = n_iter
        self.th_w = th_w
        self.compute_ll = compute_ll
        self.fit_intercept = fit_intercept
    def compute_log_likelihood(self,X,Y):
        ll =  0.5 * X.shape[1] * np.log(self.lambda_)\
            + 0.5 * X.shape[0] * np.log(self.alpha_)\
            - 0.5 * self.alpha_ *  np.sum((Y - np.dot(X, self.coef_))**2)\
            - self.lambda_ * np.dot(self.coef_.T,self.coef_)\
            - 0.5 * _fast_logdet(self.sigma_)\
            - 0.5 * X.shape[0] * np.log(2*np.pi)
        return ll
        ll =  0.5 * X.shape[1] * np.log(self.lambda_)\
            + 0.5 * X.shape[0] * np.log(self.alpha_)\
            - 0.5 * self.alpha_ *  np.sum((Y - np.dot(X, self.coef_))**2)\
            - self.lambda_ * np.dot(self.coef_.T,self.coef_)\
            - 0.5 * _fast_logdet(self.sigma_)\
            - 0.5 * X.shape[0] * np.log(2*np.pi)
        return ll
    def fit(self, X, Y, **params):
        """
    Parameters
    ----------
        Parameters
        ----------
        X : numpy array of shape [n_samples,n_features]
            Training data
    Returns
    -------
        Y : numpy array of shape [n_samples]
            Target values
        Returns
        X = np.asanyarray(X, dtype=np.float)
        Y = np.asanyarray(Y, dtype=np.float)
<<<<<<< REMOTE
X, Y = self._center_data (X, Y)
=======
n_samples, n_features = X.shape
>>>>>>> LOCAL
        -------
        self : returns an instance of self.
        ### "Dummy" initialization of the values of the parameters
        self.alpha_ = 1./np.var(Y)
        self.lambda_ = 1.0
        self.log_likelihood_ = []
        U, S, V = linalg.svd(X, full_matrices=False)
        self.eigen_vals_ = S**2
        self.X_XT = np.dot(X,X.T)
        self.XT_Y = np.dot(X.T,Y)
        ### Convergence loop of the bayesian ridge regression
        for iter_ in range(self.n_iter):
            ### Compute mu and sigma (using Woodbury matrix identity)
            self.sigma_ =  np.dot(linalg.pinv(np.eye(n_samples)/self.alpha_ +
                                  self.X_XT/self.lambda_), X/self.lambda_)
            self.sigma_ = - np.dot(X.T/self.lambda_, self.sigma_)
            self.sigma_.flat[::(self.sigma_.shape[1]+1)] += 1./self.lambda_
            self.coef_ = self.alpha_ *np.dot(self.sigma_,self.XT_Y)
            ### Update alpha and lambda
            self.gamma_ =  np.sum((self.alpha_ * self.eigen_vals_)\
                            /(self.lambda_ + self.alpha_ * self.eigen_vals_))
            self.lambda_ = self.gamma_ / np.dot(self.coef_.T,self.coef_)
            self.alpha_ = (n_samples - self.gamma_)\
                          /np.sum((Y - np.dot(X, self.coef_))**2)
            if self.compute_ll:
                self.log_likelihood_.append(self.compute_log_likelihood(X,Y))
                self.log_likelihood_.append(self.compute_log_likelihood(X,Y))
            ### Check for convergence
            if iter_ != 0 and np.sum(self.coef_old_ - self.coef_) < self.th_w:
                    break
                    break
            self.coef_old_ = np.copy(self.coef_)
            ### Compute mu and sigma (using Woodbury matrix identity)
            self.sigma_ =  np.dot(linalg.pinv(np.eye(n_samples)/self.alpha_ +
                                  self.X_XT/self.lambda_), X/self.lambda_)
            self.sigma_ = - np.dot(X.T/self.lambda_, self.sigma_)
            self.sigma_.flat[::(self.sigma_.shape[1]+1)] += 1./self.lambda_
            self.coef_ = self.alpha_ *np.dot(self.sigma_,self.XT_Y)
            ### Update alpha and lambda
            self.gamma_ =  np.sum((self.alpha_ * self.eigen_vals_)\
                            /(self.lambda_ + self.alpha_ * self.eigen_vals_))
            self.lambda_ = self.gamma_ / np.dot(self.coef_.T,self.coef_)
            self.alpha_ = (n_samples - self.gamma_)\
                          /np.sum((Y - np.dot(X, self.coef_))**2)
            #### Compute the log likelihood
            if self.compute_ll:
                self.log_likelihood_.append(self.compute_log_likelihood(X,Y))
                self.log_likelihood_.append(self.compute_log_likelihood(X,Y))
            ### Check for convergence
            if iter_ != 0 and np.sum(self.coef_old_ - self.coef_) < self.th_w:
                    break
                    break
            self.coef_old_ = np.copy(self.coef_)
        """
        self._set_params(**params)
        X = np.asanyarray(X, dtype=np.float)
        Y = np.asanyarray(Y, dtype=np.float)
        self.intercept_ = self._ymean - np.dot(self._xmean, self.coef_)
        # Store explained variance for __str__
        self.explained_variance_ = self._explained_variance(X, Y)
        return self











class ARDRegression(LinearModel):
    """
    can't use libsvm for this.
    """
    # TODO: add intercept

    def __init__(self, n_iter=300, th_w=1.e-12, th_lb=1.e-12, compute_ll=False,
        fit_intercept=True):
        self.n_iter = n_iter
        self.th_w = th_w
        self.th_lb = th_lb
        self.compute_ll = compute_ll
        self.fit_intercept = fit_intercept


    def fit(self, X, Y, **params):
        self._set_params(**params)
        X = np.asanyarray(X, dtype=np.float)
        Y = np.asanyarray(Y, dtype=np.float)
        n_samples, n_features = X.shape

        if self.fit_intercept:
            self._xmean = X.mean(axis=0)
            self._ymean = Y.mean(axis=0)
            X = X - self._xmean
            Y = Y - self._ymean
        else:
            self._xmean = 0.
            self._ymean = 0.


        ### "Dummy" initialization of the values of the parameters
        self.alpha_ = 1./np.var(Y)
        self.lambda_ = np.ones(n_features)
        self.log_likelihood_ = []
        self.X_XT = np.dot(X,X.T)
        self.XT_Y = np.dot(X.T,Y)

        ### Convergence loop of the bayesian ridge regression
        for iter_ in range(self.n_iter):

            ### Compute mu and sigma (using Woodbury matrix identity)
            self.sigma_ =  np.dot(
                    linalg.pinv(np.eye(n_samples)/self.alpha_ +
                    np.dot(X * np.reshape(1./self.lambda_,[1,-1]),X.T)),
                    X * np.reshape(1./self.lambda_,[1,-1]))
            self.sigma_ = - np.dot(np.reshape(1./self.lambda_,[-1,1]) * X.T ,
                                                                    self.sigma_)
            self.sigma_.flat[::(self.sigma_.shape[1]+1)] += 1./self.lambda_
            self.coef_ = self.alpha_ *np.dot(self.sigma_,self.XT_Y)

            ### Update alpha and lambda
            self.gamma_ =  1. - self.lambda_*np.diag(self.sigma_)
            coef_2 = (self.coef_)**2
            self.lambda_[coef_2>self.th_lb] = self.gamma_[coef_2>self.th_lb]\
                                                   /coef_2[coef_2>self.th_lb]
            self.lambda_[coef_2 <= self.th_lb] = 1./self.th_lb
            self.alpha_ = (n_samples - self.gamma_.sum())\
                          /np.sum((Y - np.dot(X, self.coef_))**2)

            #### Compute the log likelihood
            if self.compute_ll:
                self.log_likelihood_.append(self.compute_log_likelihood(X,Y))

            ### Check for convergence
            if iter_ != 0 and np.sum(self.coef_old_ - self.coef_) < self.th_w:
                    break
            self.coef_old_ = np.copy(self.coef_)

        self.intercept_ = self._ymean - np.dot(self._xmean, self.coef_)
        # Store explained variance for __str__
        self.explained_variance_ = self._explained_variance(X, Y)
        return self




 #### Compute the log likelihood
            #if ll_bool :
                #A_ = np.eye(X.shape[1])/alpha
                #C_ = (1./beta)*np.eye(X.shape[0]) + np.dot(X,np.dot(A_,X.T))
                #ll = X.shape[0]*np.log(2*np.pi)+fast_logdet(C_)
                #ll += np.dot(Y.T,np.dot(linalg.pinv(C_),Y))
                #log_likelihood.append(-0.5*ll)

















