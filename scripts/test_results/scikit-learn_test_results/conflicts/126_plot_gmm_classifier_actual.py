"""
==================
GMM classification
==================

Demonstration of :ref:`gmm` for classification.

Plots predicted labels on both training and held out test data using a
variety of GMM classifiers on the iris dataset.

Compares GMMs with spherical, diagonal, full, and tied covariance
matrices in increasing order of performance.  Although one would
expect full covariance to perform best in general, it is prone to
overfitting on small datasets and does not generalize well to held out
test data.

On the plots, train data is shown as dots, while test data is shown as
crosses. The iris dataset is four-dimensional. Only the first two 
dimensions are shown here, and thus some points are separated in other
dimensions.
"""
# Author: Ron Weiss <ronweiss@gmail.com>, Gael Varoquaux
# License: BSD Style.

# $Id$

import pylab as pl
import matplotlib as mpl
import numpy as np

from scikits.learn import datasets
from scikits.learn.cross_val import StratifiedKFold
def make_ellipses(gmm, ax):
    for n, color in enumerate('rgb'):
        v, w = np.linalg.eigh(gmm.covars[n][:2, :2])
        u = w[0] / np.linalg.norm(w[0])
        angle = np.arctan(u[1]/u[0])
        angle = 180 * angle / np.pi # convert to degrees
        v *= 9
        ell = mpl.patches.Ellipse(gmm.means[n, :2], v[0], v[1], 180 + angle,
                                  color=color)
        ell.set_clip_box(ax.bbox)
        ell.set_alpha(0.5)
        ax.add_artist(ell)

from scikits.learn.gmm import GMM


iris = datasets.load_iris()
# Break up the dataset into non-overlapping training (75%) and testing

# (25%) sets.
skf = StratifiedKFold(iris.target, k=4)
# Only take the first fold.
train_index, test_index = skf.__iter__().next()


X_train = iris.data[train_index]
y_train = iris.target[train_index]
X_test = iris.data[test_index]
y_test = iris.target[test_index]
pl.subplots_adjust(bottom=.01, top=0.95, hspace=.15, wspace=.05,
                   left=.01, right=.99)
pl.legend(loc='lower right', prop=dict(size=12))
  


pl.imshow(X_test.T, interpolation='nearest', aspect='auto', origin='lower')
n_classes = len(np.unique(y_train))

# Try GMMs using different types of covariances.
classifiers = dict((x, GMM(n_states=n_classes, cvtype=x))
                    for x in ['spherical', 'diag', 'tied', 'full'])

n_classifiers = len(classifiers)

pl.figure(figsize=(3*n_classifiers/2, 6))

for index, (name, classifier) in enumerate(classifiers.iteritems()):
    # Since we have class labels for the training data, we can
    # initialize the GMM parameters in a supervised manner.
    classifier.means = [X_train[y_train == i, :].mean(axis=0)
                        for i in xrange(n_classes)]

    # Train the other parameters using the EM algorithm.
    classifier.fit(X_train, init_params='wc', n_iter=20)

    y_train_pred = classifier.predict(X_train)
    train_accuracy  = np.mean(y_train_pred.ravel() == y_train.ravel()) * 100

    h = pl.subplot(n_classifiers + 1, 3, 3 + 3 * index + 1)
    pl.plot(y_train_pred)
    h.set_ylim(ylim)
    pl.ylabel(name)
    if index != n_classifiers - 1:
        h.set_xticks([])
    pl.title('train acc = %.1f' % train_accuracy)

    y_test_pred = classifier.predict(X_test)
    test_accuracy  = np.mean(y_test_pred.ravel() == y_test.ravel()) * 100

    h = pl.subplot(n_classifiers + 1, 3, 3 + 3 * index + 2)
    pl.plot(y_test_pred)
    h.set_ylim(ylim)
    if index != n_classifiers - 1:
        h.set_xticks([])
    pl.title('test acc = %.1f' % test_accuracy)
  
    h = pl.subplot(n_classifiers + 1, 3, 3 + 3 * index + 3)
    make_scatter_plot(iris.data, iris.target, classifier, h)


pl.show()

