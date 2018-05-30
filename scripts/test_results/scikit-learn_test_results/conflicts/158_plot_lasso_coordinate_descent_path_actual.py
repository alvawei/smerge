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

<<<<<<< REMOTE
from scikits.learn.glm.coordinate_descent import Lasso, ElasticNet, lasso_path, \
=======
enet_path, \
>>>>>>> LOCAL
                                    enet_path
n_samples, n_features = 100, 500


np.random.seed(0)
<<<<<<< REMOTE
################################################################################
=======
# lasso_objective_callback = IterationCallbackFunc(lasso_objective)
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# lasso = Lasso(alpha=alpha, callbacks=[lasso_objective_callback])
>>>>>>> LOCAL
eps = 1e-2 # the smaller it is the longer is the path
<<<<<<< REMOTE

=======
# print "Fitting lasso model to random data..."
>>>>>>> LOCAL
<<<<<<< REMOTE
print "Computing regularization path using the lasso..."
=======
# lasso.fit(X, y, maxit=maxit)
>>>>>>> LOCAL
start = datetime.now()
<<<<<<< REMOTE
alphas_lasso, weights_lasso = lasso_path(X, y, eps=eps)
=======
# print "Duality gap Lasso (should be small): %f" % \
>>>>>>> LOCAL
<<<<<<< REMOTE
print "This took ", datetime.now() - start
=======
#         lasso_dual_gap(X, y, lasso.coef_, alpha)[0]
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# lasso_objective = lasso_objective_callback.values
>>>>>>> LOCAL
start = datetime.now()
alphas_enet, weights_enet = enet_path(X, y, rho=0.6, eps=eps)
<<<<<<< REMOTE
print "This took ", datetime.now() - start
=======
# alpha, beta = 1, 1
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# enet_objective_callback = IterationCallbackFunc(enet_objective)
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# enet = ElasticNet(alpha=alpha, beta=beta, callbacks=[enet_objective_callback])
>>>>>>> LOCAL
<<<<<<< REMOTE
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
=======
# print "Fitting elastic net model to random data..."
>>>>>>> LOCAL
<<<<<<< REMOTE
for color, weight_lasso, weight_enet in zip(color_iter,
                            weights_lasso.T, weights_enet.T):
    pl.plot(-np.log10(alphas_lasso), weight_lasso, color)
    pl.plot(-np.log10(alphas_enet), weight_enet, color+'x')


=======
# enet.fit(X, y, maxit=maxit)
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.ylabel('weights')
=======
# print "Duality gap (should be small): %f" % \
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.title('Lasso and Elastic-Net Paths')
=======
#         enet_dual_gap(X, y, enet.coef_, alpha, beta)[0]
>>>>>>> LOCAL
<<<<<<< REMOTE
pl.legend(['Lasso','Elastic-Net'])
=======
# enet_objective = enet_objective_callback.values
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# pl.figure(-1, figsize=(8, 4))
>>>>>>> LOCAL
# # pl.clf()
# # pl.subplots_adjust(wspace=.4, right=.95)
# # pl.subplot(1, 2, 1)
# pl.plot(lasso_objective, label='Lasso')
# # pl.plot(enet_objective,  label='Elastic Net')
# pl.xlabel('Iteration')
# pl.ylabel('Cost function')
# pl.legend()
# pl.title('Convergence')
from datetime import datetime
start = datetime.now()

delta = datetime.now() - start
print 'time taken: ', delta

# print "Computing regularization path using the elastic net..."
# alphas_enet, weights_enet = enet_path(X, y, factor=0.93, n_alphas = 50,
#                                                 beta=0.5)

# pl.subplot(1, 2, 2)
for color, weight_lasso in zip(color_iter,
                            weights_lasso.T):
    pl.plot(-np.log(alphas_lasso), weight_lasso, color)
    # pl.plot(-np.log(alphas_enet), weight_enet, color+'x')

pl.axis('tight')
# pl.legend(['Lasso','Elastic-Net'])
y = np.random.randn(n_samples)

X = np.random.randn(n_samples, n_features)

################################################################################
# Fit models
################################################################################

################################################################################
# Demo path functions
pl.show()

