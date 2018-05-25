"""
=====================
Lasso and Elastic Net
=====================

Lasso and elastic net (L1 and L2 penalisation) implemented using a
coordinate descent.
"""

# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD Style.

<<<<<<< HEAD:examples/glm/plot_lasso_coordinate_descent_path.py
=======
from datetime import datetime
>>>>>>> remote:examples/plot_lasso_coordinate_descent_path.py
from itertools import cycle
import numpy as np
import pylab as pl

<<<<<<< HEAD:examples/glm/plot_lasso_coordinate_descent_path.py
from scikits.learn.glm import lasso_path, enet_path
=======
from scikits.learn.glm.coordinate_descent import lasso_path, enet_path

n_samples, n_features, maxit = 5, 10, 30
>>>>>>> remote:examples/plot_lasso_coordinate_descent_path.py

n_samples, n_features = 100, 10
np.random.seed(0)
y = np.random.randn(n_samples)
X = np.random.randn(n_samples, n_features)

################################################################################
# Fit models
################################################################################

################################################################################
# Demo path functions
################################################################################

eps = 1e-2 # the smaller it is the longer is the path

print "Computing regularization path using the lasso..."
<<<<<<< HEAD:examples/glm/plot_lasso_coordinate_descent_path.py
models = lasso_path(X, y, eps=eps)
=======
start = datetime.now()
models = lasso_path(X, y, eps=eps, intercept=False)
print "This took ", datetime.now() - start
>>>>>>> remote:examples/plot_lasso_coordinate_descent_path.py
alphas_lasso = np.array([model.alpha for model in models])
coefs_lasso = np.array([model.coef_ for model in models])

print "Computing regularization path using the elastic net..."
<<<<<<< HEAD:examples/glm/plot_lasso_coordinate_descent_path.py
models = enet_path(X, y, eps=eps, rho=0.6)
=======
start = datetime.now()
models = enet_path(X, y, eps=eps, intercept=False, rho=0.6)
print "This took ", datetime.now() - start
>>>>>>> remote:examples/plot_lasso_coordinate_descent_path.py
alphas_enet = np.array([model.alpha for model in models])
coefs_enet = np.array([model.coef_ for model in models])

# Display results
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
for color, coef_lasso, coef_enet in zip(color_iter,
                            coefs_lasso.T, coefs_enet.T):
    pl.plot(-np.log10(alphas_lasso), coef_lasso, color)
    pl.plot(-np.log10(alphas_enet), coef_enet, color + 'x')

pl.xlabel('-Log(lambda)')
pl.ylabel('weights')
pl.title('Lasso and Elastic-Net Paths')
pl.legend(['Lasso','Elastic-Net'])
pl.axis('tight')
pl.show()

