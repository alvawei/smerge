"""
=====================
Lasso and Elastic Net
=====================

Lasso and elastic net (L1 and L2 penalisation) implemented using a
coordinate descent.
"""

# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD Style.

from datetime import datetime
from itertools import cycle
from itertools import cycle
import numpy as np
import numpy as np
import pylab as pl

from scikits.learn.glm import lasso_path, enet_path
n_samples, n_features = 100, 10
<<<<<<< REMOTE

=======
models = lasso_path(X, y, eps=eps)
>>>>>>> LOCAL
<<<<<<< REMOTE
print "Computing regularization path using the lasso..."
=======
alphas_lasso = np.array([model.alpha for model in models])
>>>>>>> LOCAL
<<<<<<< REMOTE
start = datetime.now()
=======
coefs_lasso = np.array([model.coef_ for model in models])
>>>>>>> LOCAL
<<<<<<< REMOTE
alphas_lasso = np.array([model.alpha for model in models])
=======
models = enet_path(X, y, eps=eps, rho=0.6)
>>>>>>> LOCAL
<<<<<<< REMOTE
coefs_lasso = np.array([model.coef_ for model in models])
=======
alphas_enet = np.array([model.alpha for model in models])
>>>>>>> LOCAL
<<<<<<< REMOTE

=======
coefs_enet = np.array([model.coef_ for model in models])
>>>>>>> LOCAL
models = enet_path(X, y, eps=eps, intercept=False, rho=0.6)
<<<<<<< REMOTE
print "This took ", datetime.now() - start
=======
for color, coef_lasso, coef_enet in zip(color_iter,
                            coefs_lasso.T, coefs_enet.T):
    pl.plot(-np.log10(alphas_lasso), coef_lasso, color)
    pl.plot(-np.log10(alphas_enet), coef_enet, color + 'x')


>>>>>>> LOCAL
alphas_enet = np.array([model.alpha for model in models])
coefs_enet = np.array([model.coef_ for model in models])
for color, coef_lasso, coef_enet in zip(color_iter,
                            coefs_lasso.T, coefs_enet.T):
    pl.plot(-np.log10(alphas_lasso), coef_lasso, color)
    pl.plot(-np.log10(alphas_enet), coef_enet, color + 'x')


# Display results
color_iter = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
pl.xlabel('-Log(lambda)')
pl.ylabel('weights')
pl.title('Lasso and Elastic-Net Paths')
pl.legend(['Lasso','Elastic-Net'])
pl.axis('tight')
pl.show()

