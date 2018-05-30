"""
================================
Covertype dataset with dense SGD
================================

Benchmark stochastic gradient descent (SGD), Liblinear, and Naive Bayes on the forest covertype dataset of Blackard, Jock, and Dean [1]. The dataset comprises 581,012 samples. It is low-dimensional with 54 features and a sparsity of approx. 23%. Here, we consider the task of predicting class 1 (spruce/fir). The classification performance of SGD is competitive with Liblinear while being two orders of magnitude faster to train::

    [..]
    Classification performance:
    ===========================

    Classifier   train-time test-time error-rate
    --------------------------------------------
    Liblinear     15.5057s   0.0481s     0.2305  
    GNB           2.8415s    0.1738s     0.3633  
    SGD           0.2402s    0.0048s     0.2300 
  
The same task has been used in a number of papers including:

 * `"SVM Optimization: Inverse Dependence on Training Set Size"
   <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.139.2112>`_
   S. Shalev-Shwartz, N. Srebro - In Proceedings of ICML '08.

 * `"Pegasos: Primal estimated sub-gradient solver for svm" 
   <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.74.8513>`_
   S. Shalev-Shwartz, Y. Singer, N. Srebro - In Proceedings of ICML '07.

 * `"Training Linear SVMs in Linear Time"
   <www.cs.cornell.edu/People/tj/publications/joachims_06a.pdf>`_
   T. Joachims - In SIGKDD '06

[1] http://archive.ics.uci.edu/ml/datasets/Covertype

To run this example use your favorite python shell::

  % ipython examples/sgd/covertype_dense_sgd.py

"""
from __future__ import division

print __doc__

# Author: Peter Prettenhoer <peter.prettenhofer@gmail.com>
# License: BSD Style.

# $Id$

from time import time
import sys
import os
import numpy as np

from scikits.learn.svm import LinearSVC
from scikits.learn.sgd import SGD
from scikits.learn.naive_bayes import GNB
from scikits.learn import metrics

######################################################################
## Download the data, if not already on disk 
if not os.path.exists('covtype.data.gz'):
    # Download the data
    import urllib
    print "Downloading data, Please Wait (11MB)"
    opener = urllib.urlopen(
        'http://archive.ics.uci.edu/ml/' \
        'machine-learning-databases/covtype/covtype.data.gz')
    open('covtype.data.gz', 'wb').write(opener.read())

######################################################################
## Load dataset
print("loading dataset...")
data = np.loadtxt('covtype.data.gz', delimiter=",")
X = data[:, :-1]

# class 1 vs. all others. 
y = np.ones(data.shape[0]) * -1.0
y[np.where(data[:, -1] == 1)] = 1.0

######################################################################
## Create train-test split (T. Joachims, 2006)
print("creating train-test split...")
idx = np.arange(data.shape[0])
np.random.seed(13)
np.random.shuffle(idx)
train_idx = idx[:522911]
test_idx = idx[522911:]

X_train = X[train_idx]
y_train = y[train_idx]
X_test = X[test_idx]
y_test = y[test_idx]

######################################################################
## Standardize first 10 features (=numerical)
mean = X_train.mean(axis=0)
std = X_train.std(axis=0)
mean[10:] = 0.0
std[10:] = 1.0
X_train = (X_train-mean) / std
X_test = (X_test-mean) / std

######################################################################
## Print dataset statistics
print("")
print("")
print("Dataset statistics:")
print("===================")
print("%s %d" % ("number of features:".ljust(25),
                 X_train.shape[1]))
print("%s %d" % ("number of classes:".ljust(25),
                 np.unique(y_train).shape[0]))
print("%s %d" % ("number of train samples:".ljust(25),
                 train_idx.shape[0]))
print("%s %d" % ("number of test samples:".ljust(25),
                 test_idx.shape[0]))
print("")
print("training classifiers...")
print("")

######################################################################
## Benchmark classifiers
def benchmark(clf):
    t0 = time()
    clf.fit(X_train, y_train)
    train_time = time() - t0
    t0 = time()
    pred = clf.predict(X_test)
    test_time = time() - t0
    err = metrics.zero_one(y_test, pred) / float(pred.shape[0])
    return err, train_time, test_time

######################################################################
## Train Liblinear model
libsvm_parameters = {
    'loss': 'l2',
    'penalty': 'l2',
    'C': 1000,
    'dual': False,
    'eps': 1e-3,
    }
libsvm_res = benchmark(LinearSVC(**libsvm_parameters))
libsvm_err, libsvm_train_time, libsvm_test_time = libsvm_res

######################################################################
## Train SGD model
sgd_parameters = {
    'alpha': 0.001,
    'n_iter': 2,
    }
sgd_err, sgd_train_time, sgd_test_time = benchmark(SGD(**sgd_parameters))

######################################################################
## Train GNB model
gnb_err, gnb_train_time, gnb_test_time = benchmark(GNB())


######################################################################
## Print classification performance
print("")
print("Classification performance:")
print("===========================")
print("")
def print_row(clf_type, train_time, test_time, err):
    print("%s %s %s %s" % (clf_type.ljust(12),
                           ("%.4fs" % train_time).center(10),
                           ("%.4fs" % test_time).center(10),
                           ("%.4f" % err).center(10)))

print("%s %s %s %s" % ("Classifier  ", "train-time", "test-time", "error-rate"))
print("-" * 44)
print_row("Liblinear", libsvm_train_time, libsvm_test_time, libsvm_err)
print_row("GNB", gnb_train_time, gnb_test_time, gnb_err)
print_row("SGD", sgd_train_time, sgd_test_time, sgd_err)
print("")
print("")
