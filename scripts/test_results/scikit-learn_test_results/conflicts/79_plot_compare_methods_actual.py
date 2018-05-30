"""
=========================================
 S-curve example with various LLE methods
=========================================

An illustration of dimensionality reduction
with locally linear embedding and its variants
"""

# Author: Jake Vanderplas -- <vanderplas@astro.washington.edu>

print __doc__

from time import time

import numpy
import pylab
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import NullFormatter

from scikits.learn import manifold, datasets

<<<<<<< REMOTE
X, color = datasets.samples_generator.make_s_curve(1000)
=======
X, color = datasets.samples_generator.s_curve(1000)
=======
X, color = datasets.samples_generator.s_curve(n_points)
>>>>>>> LOCAL
n_neighbors = 15
out_dim = 2

methods = ['standard', 'ltsa', 'hessian', 'modified']

fig = pylab.figure(figsize=(8, 12))

try:
    # compatibility matplotlib < 1.0
    ax = fig.add_subplot(321, projection='3d')
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=color, cmap=pylab.cm.Spectral)
    ax.view_init(4, -72)
except:
    ax = fig.add_subplot(321, projection='3d')
    ax.scatter(X[:, 0], X[:, 2], c=color, cmap=pylab.cm.Spectral)

ax.set_title('Original Data')

for i, method in enumerate(methods):
    t0 = time()
    Y, err = manifold.locally_linear_embedding(
        X, n_neighbors, out_dim, eigen_solver='arpack', method=method)
    t1 = time()
    print "%s: %.2g sec" % (methods[i], t1 - t0)
    print ' err = %.2e' % err
    ax = fig.add_subplot(322 + i)
    ax.scatter(Y[:, 0], Y[:, 1], c=color, cmap=pylab.cm.Spectral)
    ax.set_title("%s (%.2g sec)" % (labels[i], t1 - t0))
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())



pylab.show()

