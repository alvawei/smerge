"""
======================================================
Classification of text documents using sparse features
======================================================

This is an example showing how the scikit-learn can be used to classify
documents by topics using a bag-of-words approach. This example uses
a scipy.sparse matrix to store the features instead of standard numpy arrays.

The dataset used in this example is the 20 newsgroups dataset and should be
downloaded from the http://mlcomp.org (free registration required):

  http://mlcomp.org/datasets/379

Once downloaded unzip the arhive somewhere on your filesystem. For instance in::

  % mkdir -p ~/data/mlcomp
  % cd  ~/data/mlcomp
  % unzip /path/to/dataset-379-20news-18828_XXXXX.zip

You should get a folder ``~/data/mlcomp/379`` with a file named ``metadata`` and
subfolders ``raw``, ``train`` and ``test`` holding the text documents organized by
newsgroups.

Then set the ``MLCOMP_DATASETS_HOME`` environment variable pointing to
the root folder holding the uncompressed archive::

  % export MLCOMP_DATASETS_HOME="~/data/mlcomp"

Then you are ready to run this example using your favorite python shell::

  % ipython examples/mlcomp_sparse_document_classification.py

"""
# Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: Simplified BSD

from time import time
import sys
import os
import numpy as np
import scipy.sparse as sp
import pylab as pl

from scikits.learn.datasets import load_mlcomp
from scikits.learn.feature_extraction.text.sparse import Vectorizer
from scikits.learn.svm.sparse import LinearSVC
from scikits.learn.metrics import confusion_matrix
from scikits.learn.metrics import f1_score
from scikits.learn.metrics import precision
from scikits.learn.metrics import recall

if 'MLCOMP_DATASETS_HOME' not in os.environ:
    print "Please follow those instructions to get started:"
    print __doc__
    sys.exit(0)

# Load the training set
print "Loading 20 newsgroups training set... "
news_train = load_mlcomp('20news-18828', 'train')
print news_train.DESCR
print "%d documents" % len(news_train.filenames)
print "%d categories" % len(news_train.target_names)

print "Extracting features from the dataset using a sparse vectorizer"
t0 = time()
vectorizer = Vectorizer()
X_train = vectorizer.fit_transform((open(f).read() for f in news_train.filenames))
print "done in %fs" % (time() - t0)
print "n_samples: %d, n_features: %d" % X_train.shape
assert sp.issparse(X_train)
y_train = news_train.target

print "Training a linear SVM (hinge loss and L2 regularizer)..."
parameters = {
    'loss': 'l2',
    'penalty': 'l2',
    'C': 10,
    'dual': False,
    'eps': 1e-4,
}
print "parameters:", parameters
t0 = time()
clf = LinearSVC(**parameters).fit(X_train, y_train)
print "done in %fs" % (time() - t0)
print "Percentage of non zeros coef: %f" % (np.mean(clf.coef_ != 0) * 100)

print "Loading 20 newsgroups test set... "
news_test = load_mlcomp('20news-18828', 'test')
t0 = time()
print "done in %fs" % (time() - t0)

print "Predicting the labels of the test set..."
print "%d documents" % len(news_test.filenames)
print "%d categories" % len(news_test.target_names)

print "Extracting features from the dataset using the same vectorizer"
t0 = time()
X_test = vectorizer.transform((open(f).read() for f in news_test.filenames))
y_test = news_test.target
print "done in %fs" % (time() - t0)
print "n_samples: %d, n_features: %d" % X_test.shape

print "Predicting the outcomes of the testing set"
t0 = time()
pred = clf.predict(X_test)
print "done in %fs" % (time() - t0)
print "precision: %0.3f" % precision(y_test, pred)
print "recall: %0.3f" % recall(y_test, pred)
print "f1_score: %0.3f" % f1_score(y_test, pred)

cm = confusion_matrix(y_test, pred)
print "Confusion matrix:"
print cm

# Show confusion matrix
pl.matshow(cm)
pl.title('Confusion matrix')
pl.colorbar()
pl.show()
