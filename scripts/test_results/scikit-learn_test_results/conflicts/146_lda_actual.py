import exceptions, warnings

import numpy as np
import scipy.linalg as linalg

from .base import BaseEstimator, ClassifierMixin

class LDA(BaseEstimator, ClassifierMixin):
    """
    Linear Discriminant Analysis (LDA)
    Parameters
    ----------
    X : array-like, shape = [nsamples, nfeatures]
        Training vector, where nsamples in the number of samples and
        nfeatures is the number of features.
    y : array, shape = [nsamples]
        Target vector relative to X
    priors : array, optional, shape = [n_classes]
        Priors on classes
    use_svd : bool, optional
         Specify if the SVD from scipy should be used.
    Attributes
    ----------
    `means_` : array-like, shape = [n_classes, n_features]
        Class means
    `xbar_` : float, shape = [n_features]
        Over all mean
    Methods
    -------
    fit(X, y) : self
        Fit the model
    predict(X) : array
        Predict using the model.
    Examples
    --------
    >>> X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    >>> y = np.array([1, 1, 1, 2, 2, 2])
    >>> clf = LDA()
    >>> clf.fit(X, y)
    LDA(priors=None,
        use_svd=True)
    >>> print clf.predict([[-0.8, -1]])
    [1]
    See also
    --------
    QDA
    """
    def __init__(self, priors=None, use_svd=True):
        #use_svd : if True, use linalg.svd alse use computational
        #          trick with covariance matrix
        if not priors is None:
            self.priors = np.asarray(priors)
        else: self.priors = None
        self.use_svd = use_svd
    def _svd(self, X):
        #computational trick to compute svd. U, S, V=linalg.svd(X)
        K = np.dot(X.T, X)
        S, V = linalg.eigh(K)
        S = np.sqrt(np.maximum(S, 1e-30))
        S_sort = -np.sort(-S)[:X.shape[0]]
        S_argsort = np.argsort(-S).tolist()
        V = V.T[S_argsort, :]
        V = V[:X.shape[0], :]
        return S_sort, V
    def predict(self, X):
<<<<<<< REMOTE
"""
=======
"""
>>>>>>> LOCAL
<<<<<<< REMOTE
This function does classification on an array of test vectors X.
=======
This function does classification on an array of test vectors X.
>>>>>>> LOCAL
<<<<<<< REMOTE
The predicted class C for each sample in X is returned.
=======
The predicted class C for each sample in X is returned.
>>>>>>> LOCAL
<<<<<<< REMOTE
Parameters
=======
Parameters
>>>>>>> LOCAL
<<<<<<< REMOTE
----------
=======
----------
>>>>>>> LOCAL
<<<<<<< REMOTE
X : array-like, shape = [n_samples, n_features]
=======
X : array-like, shape = [n_samples, n_features]
>>>>>>> LOCAL
<<<<<<< REMOTE
Returns
=======
Returns
>>>>>>> LOCAL
<<<<<<< REMOTE
-------
=======
-------
>>>>>>> LOCAL
<<<<<<< REMOTE
C : array, shape = [n_samples]
=======
C : array, shape = [n_samples]
>>>>>>> LOCAL
<<<<<<< REMOTE
"""
=======
"""
>>>>>>> LOCAL
<<<<<<< REMOTE
probas = self.decision_function(X)
=======
probas = self.decision_function(X)
>>>>>>> LOCAL
        y_pred = self.classes[probas.argmax(1)]
        return y_pred
    def predict_proba(self, X):
<<<<<<< REMOTE
"""
=======
"""
>>>>>>> LOCAL
<<<<<<< REMOTE
This function return posterior probabilities of classification
=======
This function return posterior probabilities of classification
>>>>>>> LOCAL
<<<<<<< REMOTE
according to each class on an array of test vectors X.
=======
according to each class on an array of test vectors X.
>>>>>>> LOCAL
<<<<<<< REMOTE
Parameters
=======
Parameters
>>>>>>> LOCAL
<<<<<<< REMOTE
----------
=======
----------
>>>>>>> LOCAL
<<<<<<< REMOTE
X : array-like, shape = [n_samples, n_features]
=======
X : array-like, shape = [n_samples, n_features]
>>>>>>> LOCAL
<<<<<<< REMOTE
Returns
=======
Returns
>>>>>>> LOCAL
<<<<<<< REMOTE
-------
=======
-------
>>>>>>> LOCAL
<<<<<<< REMOTE
C : array, shape = [n_samples, n_classes]
=======
C : array, shape = [n_samples, n_classes]
>>>>>>> LOCAL
<<<<<<< REMOTE
"""
=======
"""
>>>>>>> LOCAL
<<<<<<< REMOTE
values = self.decision_function(X)
=======
values = self.decision_function(X)
>>>>>>> LOCAL
<<<<<<< REMOTE
likelihood = np.exp(values - values.min(axis=1)[:, np.newaxis])
=======
likelihood = np.exp(values - values.min(axis=1)[:, np.newaxis])
>>>>>>> LOCAL
<<<<<<< REMOTE
# compute posterior probabilities
=======
# compute posterior probabilities
>>>>>>> LOCAL
<<<<<<< REMOTE
return likelihood / likelihood.sum(axis=1)[:, np.newaxis]
=======
return likelihood / likelihood.sum(axis=1)[:, np.newaxis]
>>>>>>> LOCAL
        X = np.asanyarray(X)
        scaling = self.scaling
        # Remove overall mean (center) and scale
        # a) data
        X = np.dot(X - self.xbar_, scaling)
        # b) centers
        dm = np.dot(self.means_ - self.xbar_, scaling)
        # for each class k, compute the linear discrinant function(p. 87 Hastie)
        # of sphered (scaled data)
        # take exp of min dist
        dist = np.exp(-dist + dist.min(1).reshape(X.shape[0], 1))
        # normalize by p(x)=sum_k p(x|k)
        probas = dist / dist.sum(1).reshape(X.shape[0], 1)
        # classify according to the maximun a posteriori
        return probas

















