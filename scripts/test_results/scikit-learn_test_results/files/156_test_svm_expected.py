"""
Testing for Support Vector Machine

TODO: remove hardcoding numerical results when possible
"""

import numpy as np
from scikits.learn import svm, datasets
from numpy.testing import *

# test sample 1
X =  [[-2,-1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1]]
Y =  [1, 1, 1, 2, 2, 2]
T =  [[-1,-1], [2, 2], [3, 2]]
true_result = [1, 2, 2]

# test sample 2
X2 = [[0, 0, 0], [1, 1, 1], [2, 0, 0, ],
      [0, 0, 2], [3, 3, 3]]
Y2 = [1, 2, 2, 2, 3]
T2 = [[-1, -1, -1], [1, 1, 1], [2, 2, 2]]
true_result2 = [1, 2, 3]


def test_CSVC():
    """
    C_SVC algorithm and linear kernel.

    We test this on two datasets, the first one with two classes and
    the second one with three classes. We check for predicted values
    and estimated parameters.

    TODO: check with different parameters of C, nonlinear kernel
    """

    clf = svm.SVC(kernel='linear')
    clf.fit(X, Y)
    pred = clf.predict(T)
    assert_array_equal(clf.dual_coef_, [[ 0.25, -.25]])
    assert_array_equal(clf.support_, [[-1,-1], [1, 1]])
    assert_array_equal(clf.intercept_, [0.])
    assert_array_equal(pred, true_result)

    # the same with other dataset
    clf.fit(X2, Y2)
    pred = clf.predict(T2)
    assert_array_almost_equal(clf.dual_coef_,
                              [[ .99, -.006, -.49, -.49, -.07],
                               [ .072, .16, 0, 0, -.16]], decimal=2)
    # TODO: why are we getting all the dataset as support vectors
    assert_array_equal(clf.support_,
                       [[ 0.,  0.,  0.],
                        [ 1.,  1.,  1.],
                        [ 2.,  0.,  0.],
                        [ 0.,  0.,  2.],
                        [ 3.,  3.,  3.]])
    assert_array_equal(pred, true_result2)

def test_precomputed():
    """
    SVC with a precomputed kernel.

    We test it with a toy dataset and with iris.
    """
    clf = svm.SVC(kernel='precomputed')
    # just a linear kernel
    K = np.dot(X, np.array(X).T)
    clf.fit(K, Y)
    # gram matrix
    KT = np.dot(T, np.array(X).T)
    pred = clf.predict(KT)

    assert_array_equal(clf.dual_coef_, [[0.25, -.25]])
    assert_array_equal(clf.intercept_, [0])
    assert_array_almost_equal(clf.support_, [[2], [4]])
    assert_array_equal(pred, true_result)


    # same as before, but using function instead of the kernel
    # matrix. kernel is just a linear kernel
    kfunc = lambda x, y: np.dot(x, y.T)
    clf = svm.SVC(kernel=kfunc)
    clf.fit(X, Y)
    pred = clf.predict(T)

    assert_array_equal(clf.dual_coef_, [[0.25, -.25]])
    assert_array_equal(clf.intercept_, [0])
    assert_array_almost_equal(clf.support_, [[2], [4]])
    assert_array_equal(pred, true_result)

    # test a precomputed kernel with the iris dataset
    clf = svm.SVC(kernel='precomputed')
    iris = datasets.load_iris()
    K = np.dot(iris.data, iris.data.T)
    clf.fit(K, iris.target)
    pred = clf.predict(K)
    assert_almost_equal(np.mean(pred == iris.target), .99, decimal=2)


def test_SVR():
    """
    Test Support Vector Regression
    """

    clf = svm.SVR(kernel='linear')
    clf.fit(X, Y)
    pred = clf.predict(T)

    assert_array_almost_equal(clf.dual_coef_, [[-0.1, 0.1]])
    assert_array_almost_equal(clf.coef_, [[0.2, 0.2]])
    assert_array_almost_equal(clf.support_, [[-1, -1], [1, 1]])
    assert_array_almost_equal(clf.intercept_, [1.5])
    assert_array_almost_equal(pred, [1.1, 2.3, 2.5])

    # the same with kernel='rbf'
    clf = svm.SVR(kernel='rbf')
    clf.fit(X, Y)
    pred = clf.predict(T)

    assert_array_almost_equal(clf.dual_coef_,
                              [[-0.01441007, -0.51530606, -0.01365979,
                                 0.51569493, 0.01387495, 0.01380604]])
    assert_raises(NotImplementedError, lambda: clf.coef_)
    assert_array_almost_equal(clf.support_, X)
    assert_array_almost_equal(clf.intercept_, [ 1.49997261])
    assert_array_almost_equal(pred, [ 1.10001274,  1.86682485,  1.73300377])


def test_oneclass():
    """
    Test OneClassSVM
    """
    clf = svm.OneClassSVM()
    clf.fit(X, Y)
    pred = clf.predict(T)

    assert_array_almost_equal(pred, [1, -1, -1])
    assert_array_almost_equal(clf.intercept_, [-1.3514943])
    assert_array_almost_equal(clf.dual_coef_, [[ 0.75061969,  0.74938031,  0.74996915,  0.75003085]])
    assert_raises(NotImplementedError, lambda: clf.coef_)


def test_tweak_params():
    """
    Make sure some tweaking of parameters works.

    We change clf.dual_coef_ at run time and expect .predict() to change
    accordingly. Notice that this is not trivial since it involves a lot
    of C/Python copying in the libsvm bindings.

    The success of this test ensures that the mapping between libsvm and
    the python classifier is complete.
    """
    clf = svm.SVC(kernel='linear')
    clf.fit(X, Y)
    assert_array_equal(clf.dual_coef_, [[.25, -.25]])
    assert_array_equal(clf.predict([[-.1, -.1]]), [1])
    clf.dual_coef_ = np.array([[.0, 1.]])
    assert_array_equal(clf.predict([[-.1, -.1]]), [2])


def test_probability():
    """
    Predict probabilities using SVC

<<<<<<< HEAD:scikits/learn/tests/test_svm.py
    FIXME: is it harmless that we obtain slightly different results on
    different operating systems ? (that is why we only check for 1
    decimal precission)
    TODO: test also on an example with intercept != 0
=======
    This uses cross validation, so we use a slightly bigger testing
    set.
>>>>>>> 2f4844ca54934b842fd76a5fe38b2c4de090b666:scikits/learn/tests/test_svm.py
    """
    from scikits.learn import datasets
    iris = datasets.load_iris()

    clf = svm.SVC(probability=True)
    clf.fit(iris.data, iris.target)

    # predict on a simple dataset
    T = [[0, 0, 0, 0],
         [2, 2, 2, 2]]
    assert_array_almost_equal(clf.predict_proba(T),
                [[ 0.993,  0.003,  0.002],
                 [ 0.740,  0.223  ,  0.035]],
                 decimal=2)

    # make sure probabilities sum to one
    pprob = clf.predict_proba(X)
    assert_array_almost_equal( pprob.sum(axis=1),
                               np.ones(len(X)))


def test_margin():
    """
    Test predict_margin
    TODO: more tests
    """
    clf = svm.SVC()
    clf.fit(X, Y)
    assert_array_almost_equal(clf.predict_margin(T),
                              [[ 0.976],
                               [-0.939],
                               [-0.619]],
                              decimal=3)


def test_weight():
    """
    Test class weights
    """
    clf = svm.SVC()
    # we give a small weights to class 1
    clf.fit(X, Y, {1: 0.1})
    # so all predicted values belong to class 2
    assert_array_almost_equal(clf.predict(X), [2]*6)


def test_error():
    """
    Test that it gives proper exception on deficient input
    """
    # impossible value of nu
    clf = svm.SVC(impl='nu_svc', kernel='linear', nu=0.0)
    assert_raises(ValueError, clf.fit, X, Y)

    Y2 = Y[:-1] # wrong dimensions for labels
    assert_raises(ValueError, svm.SVC, X, Y2)

    # Test with arrays that are non-contiguous.
    Xt = np.array(X).transpose()
    Yt = [1, 2]
    clf = svm.SVC()
    clf.fit(Xt, Yt)
    assert_array_equal(clf.predict(T), [1, 2, 2])


def test_LinearSVC():
    """
    Test basic routines using LinearSVC
    """
    clf = svm.LinearSVC().fit(X, Y)

    assert_array_equal(clf.predict(T), true_result)
    assert_array_almost_equal(clf.intercept_, [0], decimal=5)

    # the same with l1 penalty
    clf = svm.LinearSVC(penalty='l1', dual=False).fit(X, Y)
    assert_array_equal(clf.predict(T), true_result)

    # l2 penalty with dual formulation
    clf = svm.LinearSVC(penalty='l2', dual=True).fit(X, Y)
    assert_array_equal(clf.predict(T), true_result)

    #
    clf = svm.LinearSVC(penalty='l2', loss='l1', dual=True).fit(X, Y)
    assert_array_equal(clf.predict(T), true_result)


def test_coef_and_intercept_SVC_vs_LinearSVC():
    """
    Test that SVC and LinearSVC return the same coef_ and intercept_
    """
    svc = svm.SVC(kernel='linear', C=1).fit(X, Y)
    linsvc = svm.LinearSVC(C=1, penalty='l2', loss='l1', dual=True).fit(X, Y)

    assert_array_equal(linsvc.coef_.shape, svc.coef_.shape)
    assert_array_almost_equal(linsvc.coef_, svc.coef_, decimal=5)
    assert_array_almost_equal(linsvc.intercept_, svc.intercept_, decimal=5)

