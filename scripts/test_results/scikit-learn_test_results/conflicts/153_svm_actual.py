import numpy as np
import _libsvm
import _liblinear

























        







###
# Public API
# No processing should go into these classes

class SVC(BaseLibsvm):
    """
    Classification using Support Vector Machines.
    This class implements the most common classification methods
    (C-SVC, Nu-SVC) using support vector machines.
    Parameters
    ----------
    impl : string, optional
        SVM implementation to choose from. This refers to different
        formulations of the SVM optimization problem.
        Can be one of 'c_svc', 'nu_svc'. By default 'c_svc' will be chosen.
    nu : float, optional
        An upper bound on the fraction of training errors and a lower
        bound of the fraction of support vectors. Should be in the
        interval (0, 1].  By default 0.5 will be taken.  Only
        available if impl='nu_svc'
    kernel : string, optional
         Specifies the kernel type to be used in the algorithm.
         one of 'linear', 'poly', 'rbf', 'sigmoid', 'precomputed'.
         If none is given 'rbf' will be used.
    degree : int, optional
        degree of kernel function
        is significant only in poly, rbf, sigmoid
    gamma : float, optional (default=0.0)
        kernel coefficient for rbf
    C : float, optional (default=1.0)
        penalty parameter C of the error term.
    probability: boolean, optional (False by default)
        enable probability estimates. This must be enabled prior
        to calling prob_predict.
    coef0 : float, optional
        independent term in kernel function. It is only significant
        in poly/sigmoid.
    Attributes
    ----------
    `support_` : array-like, shape = [nSV, nfeatures]
        Support vectors.
    `dual_coef_` : array, shape = [nclasses-1, nSV]
        Coefficients of the support vector in the decision function.
    `coef_` : array, shape = [nclasses-1, nfeatures]
        Weights asigned to the features (coefficients in the primal
        problem). This is only available in the case of linear kernel.
    `intercept_` : array, shape = [nclasses-1]
        Constants in decision function.
    Methods
    -------
    fit(X, Y) : self
        Fit the model
    predict(X) : array
        Predict using the model.
    predict_proba(X) : array
        Return probability estimates.
    Examples
    --------
    >>> X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
    >>> Y = np.array([1, 1, 2, 2])
    >>> clf = SVC()
    >>> clf.fit(X, Y)
    SVC(kernel=rbf,
        C=1.0,
        probability=0,
        degree=3,
        shrinking=1,
        eps=0.001,
        p=0.1,
        impl=c_svc,
        cache_size=100.0,
        coef0=0.0,
        nu=0.5,
        gamma=0.25)
    >>> print clf.predict([[-0.8, -1]])
    [ 1.]
    See also
    --------
    SVR
    """
    def __init__(self, impl='c_svc', kernel='rbf', degree=3, gamma=0.0,
                 coef0=0.0,cache_size=100.0, eps=1e-3, C=1.0,nu=0.5, p=0.1,
                 shrinking=True, probability=False):
        BaseLibsvm.__init__(self, impl, kernel, degree, gamma, coef0,
                         cache_size, eps, C, nu, p,
                         shrinking, probability)







    














class SVR(BaseLibsvm):
    """
    Support Vector Regression.
    Parameters
    ----------
    impl : string, optional
        SVM implementation to choose from. This refers to different formulations
        of the SVM optimization problem. Can be one of 'epsilon_svr', 'nu_svr'.
        By default 'epsilon_svc' will be chosen.
    nu : float, optional
        An upper bound on the fraction of training errors and a lower bound of
        the fraction of support vectors. Should be in the interval (0, 1].  By
        default 0.5 will be taken.  Only available if impl='nu_svc'
    kernel : string, optional
         Specifies the kernel type to be used in the algorithm.
         one of 'linear', 'poly', 'rbf', 'sigmoid', 'precomputed'.
         If none is given 'rbf' will be used.
    degree : int, optional
        degree of kernel function
        is significant only in poly, rbf, sigmoid
    gamma : float, optional (default=0.0)
        kernel coefficient for rbf
    C : float, optional (default=1.0)
        penalty parameter C of the error term.
    probability: boolean, optional (False by default)
        enable probability estimates. This must be enabled prior
        to calling prob_predict.
    coef0 : float, optional
        independent term in kernel function. It is only significant
        in poly/sigmoid.
    Attributes
    ----------
    `support_` : array-like, shape = [nSV, nfeatures]
        Support vectors
    `dual_coef_` : array, shape = [nclasses-1, nSV]
        Coefficients of the support vector in the decision function.
    `coef_` : array, shape = [nclasses-1, nfeatures]
        Weights asigned to the features (coefficients in the primal
        problem). This is only available in the case of linear kernel.
    `intercept_` : array, shape = [nclasses-1]
        constants in decision function
    Methods
    -------
    fit(X, Y) : self
        Fit the model
    predict(X) : array
        Predict using the model.
    predict_proba(X) : array
        Return probability estimates.
    See also
    --------
    SVC
    """
    def __init__(self, kernel='rbf', degree=3, gamma=0.0, coef0=0.0,
                 cache_size=100.0, eps=1e-3, C=1.0, nu=0.5, p=0.1,
                 shrinking=True, probability=False):
        BaseLibsvm.__init__(self, 'epsilon_svr', kernel, degree, gamma, coef0,
                         cache_size, eps, C, nu, p,
                         shrinking, probability)







    











class OneClassSVM(BaseLibsvm):
    """
    Outlayer detection
    Parameters
    ----------
    kernel : string, optional
         Specifies the kernel type to be used in the algorithm. one of 'linear',
         'poly', 'rbf', 'sigmoid', 'precomputed'. If none is given 'rbf' will be
         used.
    nu : float, optional
        An upper bound on the fraction of training errors and a lower bound of
        the fraction of support vectors. Should be in the interval (0, 1].  By
        default 0.5 will be taken.  Only available if impl='nu_svc'
    degree : int, optional
        degree of kernel function. Significant only in poly, rbf, sigmoid
    gamma : float, optional (default=0.0)
        kernel coefficient for rbf.
    C : float, optional (default=1.0)
        penalty parameter C of the error term.
    probability: boolean, optional (False by default)
        enable probability estimates. Must be enabled prior to calling
        prob_predict.
    coef0 : float, optional
        independent term in kernel function. It is only significant in
        poly/sigmoid.
    Attributes
    ----------
    `support_` : array-like, shape = [nSV, nfeatures]
        Support vectors
    `dual_coef_` : array, shape = [nclasses-1, nSV]
        Coefficient of the support vector in the decision function.
    `coef_` : array, shape = [nclasses-1, nfeatures]
        Weights asigned to the features (coefficients in the primal
        problem). This is only available in the case of linear kernel.
    `intercept_` : array, shape = [nclasses-1]
        constants in decision function
    Methods
    -------
    fit(X, Y) : self
        Fit the model
    predict(X) : array
        Predict using the model.
    predict_proba(X) : array
        Return probability estimates.
    """
    def __init__(self, kernel='rbf', degree=3, gamma=0.0, coef0=0.0,
                 cache_size=100.0, eps=1e-3, C=1.0, 
                 nu=0.5, p=0.1, shrinking=True, probability=False):
        BaseLibsvm.__init__(self, 'one_class', kernel, degree, gamma, coef0,
                         cache_size, eps, C, nu, p,
                         shrinking, probability)






    





    























        






