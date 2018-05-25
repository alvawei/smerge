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
<<<<<<< HEAD
                                    enet_path, \
                                    lasso_objective, enet_objective
=======
                                    enet_path
>>>>>>> remote

n_samples, n_features = 100, 500

np.random.seed(0)
y = np.random.randn(n_samples)
X = np.random.randn(n_samples, n_features)

################################################################################
# Fit models
################################################################################

<<<<<<< HEAD
# Lasso
alpha = 1
# lasso_objective_callback = IterationCallbackFunc(lasso_objective)
# lasso = Lasso(alpha=alpha, callbacks=[lasso_objective_callback])

# print "Fitting lasso model to random data..."
# lasso.fit(X, y, maxit=maxit)

# print "Duality gap Lasso (should be small): %f" % \
#         lasso_dual_gap(X, y, lasso.coef_, alpha)[0]
# lasso_objective = lasso_objective_callback.values


# # Elastic-Net
# alpha, beta = 1, 1
# enet_objective_callback = IterationCallbackFunc(enet_objective)
# enet = ElasticNet(alpha=alpha, beta=beta, callbacks=[enet_objective_callback])

# print "Fitting elastic net model to random data..."
# enet.fit(X, y, maxit=maxit)

# print "Duality gap (should be small): %f" % \
#         enet_dual_gap(X, y, enet.coef_, alpha, beta)[0]
# enet_objective = enet_objective_callback.values

# Display results
# pl.figure(-1, figsize=(8, 4))
# # pl.clf()
# # pl.subplots_adjust(wspace=.4, right=.95)
# # pl.subplot(1, 2, 1)
# pl.plot(lasso_objective, label='Lasso')
# # pl.plot(enet_objective,  label='Elastic Net')
# pl.xlabel('Iteration')
# pl.ylabel('Cost function')
# pl.legend()
# pl.title('Convergence')

=======
>>>>>>> remote
################################################################################
# Demo path functions
################################################################################

eps = 1e-2 # the smaller it is the longer is the path

print "Computing regularization path using the lasso..."
<<<<<<< HEAD
from datetime import datetime

start = datetime.now()

alphas_lasso, weights_lasso = lasso_path(X, y, factor=0.97, n_alphas = 100)

delta = datetime.now() - start

print 'time taken: ', delta

# print "Computing regularization path using the elastic net..."
# alphas_enet, weights_enet = enet_path(X, y, factor=0.93, n_alphas = 50,
#                                                 beta=0.5)

# Display results
# pl.subplot(1, 2, 2)
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
for color, weight_lasso in zip(color_iter,
                            weights_lasso.T):
    pl.plot(-np.log(alphas_lasso), weight_lasso, color)
    # pl.plot(-np.log(alphas_enet), weight_enet, color+'x')
=======
start = datetime.now()
alphas_lasso, weights_lasso = lasso_path(X, y, eps=eps)
print "This took ", datetime.now() - start

print "Computing regularization path using the elastic net..."
start = datetime.now()
alphas_enet, weights_enet = enet_path(X, y, rho=0.6, eps=eps)
print "This took ", datetime.now() - start


# Display results
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
for color, weight_lasso, weight_enet in zip(color_iter,
                            weights_lasso.T, weights_enet.T):
    pl.plot(-np.log10(alphas_lasso), weight_lasso, color)
    pl.plot(-np.log10(alphas_enet), weight_enet, color+'x')
>>>>>>> remote

pl.xlabel('-Log(lambda)')
pl.ylabel('weights')
pl.title('Lasso and Elastic-Net Paths')
<<<<<<< HEAD
pl.axis('tight')
# pl.legend(['Lasso','Elastic-Net'])
=======
pl.legend(['Lasso','Elastic-Net'])
pl.axis('tight')
>>>>>>> remote
pl.show()

