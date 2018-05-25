"""
=====================
Lasso and Elastic Net
=====================

Lasso and elastic net (L1 and L2 penalisation) implemented using a
coordinate descent.
"""

# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD Style.

# $Id$

from datetime import datetime
from itertools import cycle
import numpy as np
import pylab as pl

from scikits.learn.glm.coordinate_descent import Lasso, ElasticNet, lasso_path, \
                                    enet_path


np.random.seed(0)
y = np.random.randn(n_samples)
X = np.random.randn(n_samples, n_features)

################################################################################
# Fit models
################################################################################

eps = 1e-2 # the smaller it is the longer is the path

start = datetime.now()
alphas_lasso, weights_lasso = lasso_path(X, y, eps=eps)
print "This took ", datetime.now() - start
start = datetime.now()
alphas_enet, weights_enet = enet_path(X, y, rho=0.6, eps=eps)
print "This took ", datetime.now() - start




pl.axis('tight')


# Display results
################################################################################
# Demo path functions
################################################################################
print "Computing regularization path using the lasso..."
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
pl.xlabel('-Log(lambda)')
pl.ylabel('weights')
pl.title('Lasso and Elastic-Net Paths')
pl.show()

