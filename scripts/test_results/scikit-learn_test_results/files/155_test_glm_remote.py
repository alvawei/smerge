import numpy as np
from numpy.testing import *
from nose.tools import *

from scikits.learn import glm

def test_toy():
    """Very simple test on a small dataset"""
    X = [[1, 0, -1.],
         [0, 0, 0],
         [0, 1, .9]]
    Y = [1, 0, -1]

    clf = glm.LeastAngleRegression().fit(X, Y, max_features=1)
    assert_array_almost_equal(clf.coef_, [0, 0, -1.2624], decimal=4)
    assert_array_almost_equal(clf.alphas_, [1.4135, 0.1510], decimal=4)
    assert_array_almost_equal(clf.alphas_.shape, clf.coef_path_.shape[1])
    assert np.linalg.norm(clf.predict(X) - Y) < 0.3
    

    clf = glm.LeastAngleRegression().fit(X, Y) # implicitly max_features=2
    assert_array_almost_equal(clf.coef_, [0, -.0816, -1.34412], decimal=4)
    assert_array_almost_equal(clf.alphas_, \
                 [ 1.41356,   .1510,   3.919e-16], decimal=4)
    assert_array_almost_equal(clf.alphas_.shape, clf.coef_path_.shape[1])
    assert_array_almost_equal(clf.predict(X), np.array(Y))

    # TODO: check that Lasso with coordinate descent finds the same
    # coefficients

def test_feature_selection():
    n_samples, n_features = 442, 100

    # deterministic test
    np.random.seed(0)

    # generate random input set
    X = np.random.randn(n_samples, n_features)

    # generate a ground truth model with only the first 10 features being non
    # zeros (the other features are not correlated to Y and should be ignored by
    # the L1 regularizer)
    coef_ = np.random.randn(n_features)
    coef_[10:] = 0.0

    # generate the grand truth Y from the model and Y
    Y = np.dot(X, coef_)
    Y += np.random.normal(Y.shape) # make some (label) noise!

    # fit the model assuming that will allready know that only 10 out of
    # n_features are contributing to Y
    clf = glm.LeastAngleRegression().fit(X, Y, max_features=10)

    # ensure that only the first 10 coefs are non zeros and the remaining set to
    # null, as in the ground thrutg model
    assert_equal((clf.coef_[:10] == 0.0).sum(), 0)
    assert_equal((clf.coef_[10:] != 0.0).sum(), 0)

    # train again, but this time without knowing in advance how many features
    # are useful:
    clf = glm.LeastAngleRegression().fit(X, Y, max_features=None)
    assert_equal((clf.coef_[:10] == 0.0).sum(), 0)
    assert_equal((clf.coef_[10:] != 0.0).sum(), 89)

    # explicitly set to zero parameters really close to zero (manual
    # thresholding)
    sparse_coef = np.where(abs(clf.coef_) < 1e-13,
                           np.zeros(clf.coef_.shape),
                           clf.coef_)

    # we find again that only the first 10 features are useful
    assert_equal((sparse_coef[:10] == 0.0).sum(), 0)
    assert_equal((sparse_coef[10:] != 0.0).sum(), 0)


def test_predict():
    """
    Just see if predicted values are close from known response.
    """
    n, m = 10, 20
    np.random.seed(0)
    X = np.random.randn(n, m)
    Y = np.random.randn(n)
    Y = Y - Y.mean() # center response

    Y_ = glm.LeastAngleRegression().fit(X, Y, intercept=False).predict(X)
    print np.linalg.norm(Y - Y_)
    assert np.linalg.norm(Y-Y_) < 1e-10


    # the same but with an intercept
    Y = Y + 10.
    Y_ = glm.LeastAngleRegression().fit(X, Y).predict(X)
    assert np.linalg.norm(Y-Y_) < 1e-10
