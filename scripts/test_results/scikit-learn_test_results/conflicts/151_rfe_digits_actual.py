"""
Recursive feature elimination
=======================================================================

A recursive feature elimination is performed prior to SVM classification.
"""

import numpy as np
from scikits.learn.svm import SVC
from scikits.learn.cross_val import StratifiedKFold, GridSearchCV
from scikits.learn import datasets
from scikits.learn.feature_selection.univariate_selection import\
UnivariateFilter,SelectKBest,f_classif
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
svc = SVC(kernel="linear", C=1)
anova_filter = UnivariateFilter(SelectKBest(k=10), f_classif)
<<<<<<< REMOTE
image_support_ = rfe.support_.reshape(digits.images[0].shape)
=======
clf = SVC(kernel="linear",C=1)
>>>>>>> LOCAL
<<<<<<< REMOTE
import pylab as pl
=======
y_pred_rfe = []
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.matshow(image_support_)
=======
y_pred_univ = []
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.colorbar()
=======
y_true = []
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.title('Voxels selected with RFE')
=======
for train, test in StratifiedKFold(y, 2):
    Xtrain, ytrain, Xtest, ytest = X[train], y[train], X[test], y[test]

    ### Fit and predict rfe
    support = rfe.fit(X[train], y[train]).support_
    y_pred_rfe.append(clf.fit(X[train,support],y[train]).predict(
          X[test,support]))

    ### Fit and predict univariate feature selection
    xr = anova_filter.fit(Xtrain, ytrain).transform(Xtrain)
    y_pred_univ.append(clf.fit(Xtrain[:,anova_filter.support_],ytrain).predict(
          Xtest[:,anova_filter.support_]))
    y_true.append(ytest)


>>>>>>> LOCAL
<<<<<<< REMOTE

=======
y_pred_univ = np.concatenate(y_pred_univ)
>>>>>>> LOCAL
<<<<<<< REMOTE
#anova_filter = UnivariateFilter(SelectKBest(k=5), f_regression)
=======
y_true = np.concatenate(y_true)
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
classif_rate_univ = np.mean(y_pred_univ == y_true) * 100
>>>>>>> LOCAL
<<<<<<< REMOTE
#y_pred_rfe = []
=======
print "Classification rate univariate: %f" % classif_rate_univ
>>>>>>> LOCAL
<<<<<<< REMOTE
#print "Classification rate : %f" % classif_rate
=======

>>>>>>> LOCAL

# unvariate feature selection











