"""
Recursive feature elimination
=======================================================================

A recursive feature elimination is performed prior to SVM classification.
"""

import numpy as np
from scikits.learn.svm import SVC
from scikits.learn.cross_val import StratifiedKFold, GridSearchCV
from scikits.learn import datasets
from scikits.learn.rfe import RFE



################################################################################
# Loading the Digits dataset
digits = datasets.load_digits()

# To apply an classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(digits.images)
X = digits.images.reshape((n_samples, -1))
y = digits.target

################################################################################
# Create the RFE object and compute a cross-validated score, compared to an
# unvariate feature selection

svc = SVC(kernel="linear", C=1)
rfe = RFE(estimator=svc, n_features=30, percentage=0.1)
image_support_ = rfe.support_.reshape(digits.images[0].shape)
import pylab as pl
pl.matshow(image_support_)
pl.colorbar()
pl.title('Voxels selected with RFE')














