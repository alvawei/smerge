
import numpy as np
import scipy.sparse as sp

from . import libsvm, liblinear
from ..base import BaseEstimator
from ..utils.extmath import safe_sparse_dot
import warnings


LIBSVM_IMPL = ['c_svc', 'nu_svc', 'one_class', 'epsilon_svr', 'nu_svr']


def _get_class_weight(class_weight, y):
    """Estimate class weights for unbalanced datasets."""
    if class_weight == 'auto':
        uy = np.unique(y)
        weight_label = np.asarray(uy, dtype=np.int32, order='C')
        weight = np.array([1.0 / np.sum(y == i) for i in uy],
                          dtype=np.float64, order='C')
        weight *= uy.shape[0] / np.sum(weight)
    else:
        if class_weight is None:
            keys = values = []
        else:
            keys = class_weight.keys()
            values = class_weight.values()
        weight = np.asarray(values, dtype=np.float64, order='C')
        weight_label = np.asarray(keys, dtype=np.int32, order='C')
    return weight, weight_label



class BaseLibSVM(BaseEstimator):
    """Base class for estimators that use libsvm as backing library

    This implements support vector machine classification and regression.
    """
    def __init__(self, impl, kernel, degree, gamma, coef0,
                 tol, C, nu, epsilon, shrinking, probability, cache_size,
                 scale_C, sparse):
        if not impl in LIBSVM_IMPL:
            raise ValueError("impl should be one of %s, %s was given" % (
                LIBSVM_IMPL, impl))
        if hasattr(kernel, '__call__'):
            self.kernel_function = kernel
            self.kernel = 'precomputed'
        else:
            self.kernel = kernel
        if not scale_C:
            warnings.warn('SVM: scale_C will be True by default in '
                          'scikit-learn 0.11', FutureWarning,
                          stacklevel=2)
        self.impl = impl
        self.degree = degree
        self.gamma = gamma
        self.coef0 = coef0
        self.tol = tol
        self.C = C
        self.nu = nu
        self.epsilon = epsilon
        self.shrinking = shrinking
        self.probability = probability
        self.cache_size = cache_size
        self.scale_C = scale_C
    def fit(self, X, y, class_weight=None, sample_weight=None):
        self._sparse = sp.isspmatrix(X) if self.sparse == "auto" else self.sparse
        fit = self._sparse_fit if self._sparse else self._dense_fit
        fit(X, y, class_weight, sample_weight)
    def predict(self, X):
        X = self._validate_for_predict(X)
        predict = self._sparse_predict if self._sparse else self._dense_predict
        return predict(X)
    def predict_proba(self, X):
        X = self._validate_for_predict(X)
        pred_proba = self._sparse_predict_proba if self._sparse \
                                                else self._dense_predict_proba
        return pred_proba(X)
    def predict_log_proba(self, X):
        """Compute the log likehoods each possible outcomes of samples in X.

        The model need to have probability information computed at training
        time: fit with attribute `probability` set to True.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]

        Returns
        -------
        X : array-like, shape = [n_samples, n_classes]
            Returns the log-probabilities of the sample for each class in
            the model, where classes are ordered by arithmetical
            order.

        Notes
        -----
        The probability model is created using cross validation, so
        the results can be slightly different than those obtained by
        predict. Also, it will meaningless results on very small
        datasets.
        """
        return np.log(self.predict_proba(X))
    @property
    def coef_(self):
        if self.kernel != 'linear':
            raise ValueError('coef_ is only available when using a '
                             'linear kernel')
        if self.dual_coef_.shape[0] == 1:
            # binary classifier
            # binary classifier
            coef = safe_sparse_dot(self.dual_coef_, self.support_vectors_)
        coef = safe_sparse_dot(self.dual_coef_, self.support_vectors_)
        # coef_ being a read-only property it's better to mark the value as
        # immutable to avoid hiding potential bugs for the unsuspecting user
<<<<<<< REMOTE
else:
=======
if sp.issparse(coef):
>>>>>>> LOCAL
        else:
            coef.flags.writeable = False
        return coef
        return coef



































class BaseLibLinear(BaseEstimator):
    """Base for classes binding liblinear (dense and sparse versions)"""
    _solver_type_dict = {
        'PL2_LLR_D0': 0,  # L2 penalty, logistic regression
        'PL2_LL2_D1': 1,  # L2 penalty, L2 loss, dual form
        'PL2_LL2_D0': 2,  # L2 penalty, L2 loss, primal form
        'PL2_LL1_D1': 3,  # L2 penalty, L1 Loss, dual form
        'MC_SVC': 4,      # Multi-class Support Vector Classification
        'PL1_LL2_D0': 5,  # L1 penalty, L2 Loss, primal form
        'PL1_LLR_D0': 6,  # L1 penalty, logistic regression
        'PL2_LLR_D1': 7,  # L2 penalty, logistic regression, dual form
        }
    def __init__(self, penalty='l2', loss='l2', dual=True, tol=1e-4, C=1.0,
                 multi_class=False, fit_intercept=True, intercept_scaling=1,
                 scale_C=False):
        self.penalty = penalty
        self.loss = loss
        self.dual = dual
        self.tol = tol
        self.C = C
        self.fit_intercept = fit_intercept
        self.intercept_scaling = intercept_scaling
        self.multi_class = multi_class
        self.scale_C = scale_C
        # Check that the arguments given are valid:
        self._get_solver_type()
    def _get_solver_type(self):
        """Find the liblinear magic number for the solver.

        This number depends on the values of the following attributes:
          - multi_class
          - penalty
          - loss
          - dual
        """
        if self.multi_class:
            solver_type = 'MC_SVC'
        if not solver_type in self._solver_type_dict:
            if self.penalty.upper() == 'L1' and self.loss.upper() == 'L1':
                error_string = ("The combination of penalty='l1' "
                    "and loss='l1' is not supported.")
            elif self.penalty.upper() == 'L2' and self.loss.upper() == 'L1':
                # this has to be in primal
                error_string = ("loss='l2' and penalty='l1' is "
                    "only supported when dual='true'.")
            else:
            solver_type = "P%s_L%s_D%d" % (
                self.penalty.upper(), self.loss.upper(), int(self.dual))
            raise ValueError('Not supported set of arguments: '
                             + error_string)
        return self._solver_type_dict[solver_type]
    def fit(self, X, y, class_weight=None):
        """Fit the model according to the given training data.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vector, where n_samples in the number of samples and
            n_features is the number of features.

        y : array-like, shape = [n_samples]
            Target vector relative to X

        class_weight : {dict, 'auto'}, optional
            Weights associated with classes. If not given, all classes
            are supposed to have weight one.

        Returns
        -------
        self : object
            Returns self.
        """
        X = atleast2d_or_csr(X, dtype=np.float64, order="C")
        y = np.asarray(y, dtype=np.int32).ravel()
        self._sparse = sp.isspmatrix(X)
        self.class_weight, self.class_weight_label = \
                     _get_class_weight(class_weight, y)
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y have incompatible shapes.\n" +
                             "X has %s samples, but y has %s." % \
                             (X.shape[0], y.shape[0]))
            raise ValueError("X and y have incompatible shapes.\n" +
                             "X has %s samples, but y has %s." % \
                             (X.shape[0], y.shape[0]))
        C = self.C
        if self.scale_C:
            C = C / float(X.shape[0])
            C = C / float(X.shape[0])
        train = liblinear.csr_train_wrap if self._sparse \
                                         else liblinear.train_wrap
        self.raw_coef_, self.label_ = train(X, y, self._get_solver_type(),
                                            self.tol, self._get_bias(), C,
                                            self.class_weight_label,
                                            self.class_weight)
        self.class_weight, self.class_weight_label = \
                     _get_class_weight(class_weight, y)
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y have incompatible shapes: %r vs %r\n"
                             "Note: Sparse matrices cannot be indexed w/"
                             "boolean masks (use `indices=True` in CV)."
                             % (X.shape, y.shape))
        C = self.C
        if self.scale_C:
            C /= float(X.shape[0])
        return self
    def predict(self, X):
        X = self._validate_for_predict(X)
        predict = liblinear.csr_predict_wrap if self._sparse \
                                             else liblinear.predict_wrap
        return predict(X, self.raw_coef_, self._get_solver_type(), self.tol,
                       self.C, self.class_weight_label, self.class_weight,
                       self.label_, self._get_bias())
        """Perform classification or regression samples in X.

        For a classification model, the predicted class for each
        sample in X is returned.  For a regression model, the function
        value of X calculated is returned.

        For an one-class model, +1 or -1 is returned.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]

        Returns
        -------
        C : array, shape = [n_samples]
        """
        X.data = np.asarray(X.data, dtype=np.float64, order='C')
        solver_type = LIBSVM_IMPL.index(self.impl)
    def decision_function(self, X):
        """Decision function value for X according to the trained model.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]

        Returns
        -------
        T : array-like, shape = [n_samples, n_class]
            Returns the decision function of the sample for each class
            in the model.
        """
        X = self._validate_for_predict(X)
        X.data = np.asarray(X.data, dtype=np.float64, order='C')
        dfunc_wrap = liblinear.csr_decision_function_wrap \
                       if self._sparse \
                       else liblinear.decision_function_wrap
        dec_func = dfunc_wrap(X, self.raw_coef_, self._get_solver_type(),
                              self.tol, self.C, self.class_weight_label,
                              self.class_weight, self.label_, self._get_bias())
        self._check_n_features(X)
            return dec_func
                 C, self.class_weight_label, self.class_weight,
        else:
                # only PL1 in dual remains
                error_string = ("penalty='l1' is only supported "
                    "when dual='false'.")
    def _check_n_features(self, X):
        n_features = self.raw_coef_.shape[1]
        if self.fit_intercept:
            n_features -= 1
        if X.shape[1] != n_features:
            raise ValueError("X.shape[1] should be %d, not %d." % (n_features,
                                                                   X.shape[1]))
    def _validate_for_predict(self, X):
        X = atleast2d_or_csr(X, dtype=np.float64, order="C")
        if self._sparse and not sp.isspmatrix(X):
            X = sp.csr_matrix(X)
            X = sp.csr_matrix(X)
        elif sp.isspmatrix(X) and not self._sparse:
            raise ValueError(
                "cannot use sparse input in %r trained on dense data"
                % type(self).__name__)
            raise ValueError(
                "cannot use sparse input in %r trained on dense data"
                % type(self).__name__)
        return X
        X = atleast2d_or_csr(X, dtype=np.float64, order="C")
        if self._sparse and not sp.isspmatrix(X):
            X = sp.csr_matrix(X)
            X = sp.csr_matrix(X)
        elif sp.isspmatrix(X) and not self._sparse:
            raise ValueError(
                "cannot use sparse input in %r trained on dense data"
                % type(self).__name__)
            raise ValueError(
                "cannot use sparse input in %r trained on dense data"
                % type(self).__name__)
        return X
    def _get_intercept_(self):
        if self.fit_intercept:
            ret = self.intercept_scaling * self.raw_coef_[:, -1]
            return ret
        return 0.0
    def _set_intercept_(self, intercept):
        self.fit_intercept = True
        intercept /= self.intercept_scaling
        intercept = intercept.reshape(-1, 1)
        self.raw_coef_ = np.hstack((self.raw_coef_[:, : -1], intercept))
    intercept_ = property(_get_intercept_, _set_intercept_)
    def _get_coef_(self):
        if self.fit_intercept:
            ret = self.raw_coef_[:, : -1].copy()
        else:
            ret = self.raw_coef_.copy()
        # mark the returned value as immutable
        # to avoid silencing potential bugs
    def _set_coef_(self, coef):
        raw_intercept = self.raw_coef_[:, -1].reshape(-1, 1)
        self.raw_coef_ = coef
        if self.fit_intercept:
            self.raw_coef_ = np.hstack((self.raw_coef_, raw_intercept))
    coef_ = property(_get_coef_, _set_coef_)
    def _get_bias(self):
        if self.fit_intercept:
            return self.intercept_scaling
        else:

































libsvm.set_verbosity_wrap(0)

