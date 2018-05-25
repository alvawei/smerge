"""K-means clustering"""

# Authors: Gael Varoquaux <gael.varoquaux@normalesup.org>
#          Thomas Rueckstiess <ruecksti@in.tum.de>
#          James Bergstra <james.bergstra@umontreal.ca>
#          Jan Schlueter <scikit-learn@jan-schlueter.de>
# License: BSD

import warnings

import numpy as np

from ..base import BaseEstimator
from ..metrics.pairwise import euclidean_distances
from ..utils import check_random_state


###############################################################################
# Initialisation heuristic

def k_init(X, k, n_local_trials=None, random_state=None, x_squared_norms=None):
    """Init k seeds according to kmeans++

    Parameters
    -----------
    X: array, shape (n_samples, n_features)
        The data to pick seeds for

    k: integer
        The number of seeds to choose

    n_local_trials: integer, optional
        The number of seeding trials for each center (except the first),
        of which the one reducing inertia the most is greedily chosen.
        Set to None to make the number of trials depend logarithmically
        on the number of seeds (2+log(k)); this is the default.

    random_state: numpy.RandomState, optional
        The generator used to initialize the centers. Defaults to numpy.random.

    x_squared_norms: array, shape (n_samples,), optional
        Squared euclidean norm of each data point. Pass it if you have it at
        hands already to avoid it being recomputed here. Default: None

    Notes
    ------
    Selects initial cluster centers for k-mean clustering in a smart way
    to speed up convergence. see: Arthur, D. and Vassilvitskii, S.
    "k-means++: the advantages of careful seeding". ACM-SIAM symposium
    on Discrete algorithms. 2007

    Version ported from http://www.stanford.edu/~darthur/kMeansppTest.zip,
    which is the implementation used in the aforementioned paper.
    """
    n_samples, n_features = X.shape
    random_state = check_random_state(random_state)

    centers = np.empty((k, n_features))

    # Set the number of local seeding trials if none is given
    if n_local_trials is None:
        # This is what Arthur/Vassilvitskii tried, but did not report
        # specific results for other than mentioning in the conclusion
        # that it helped.
        n_local_trials = 2 + int(np.log(k))

    # Pick first center randomly
    center_id = random_state.randint(n_samples)
    centers[0] = X[center_id]

    # Initialize list of closest distances and calculate current potential
    if x_squared_norms is None:
        x_squared_norms = (X ** 2).sum(axis=1)
    closest_dist_sq = euclidean_distances(
        np.atleast_2d(centers[0]), X, Y_norm_squared=x_squared_norms,
        squared=True)
    current_pot = closest_dist_sq.sum()

    # Pick the remaining k-1 points
    for c in xrange(1, k):
        # Choose center candidates by sampling with probability proportional
        # to the squared distance to the closest existing center
        rand_vals = random_state.random_sample(n_local_trials) * current_pot
        candidate_ids = np.searchsorted(closest_dist_sq.cumsum(), rand_vals)

        # Compute distances to center candidates
        distance_to_candidates = euclidean_distances(
            X[candidate_ids], X, Y_norm_squared=x_squared_norms, squared=True)

        # Decide which candidate is the best
        best_candidate = None
        best_pot = None
        best_dist_sq = None
        for trial in xrange(n_local_trials):
            # Compute potential when including center candidate
            new_dist_sq = np.minimum(closest_dist_sq,
                                     distance_to_candidates[trial])
            new_pot = new_dist_sq.sum()

            # Store result if it is the best local trial so far
            if (best_candidate is None) or (new_pot < best_pot):
                best_candidate = candidate_ids[trial]
                best_pot = new_pot
                best_dist_sq = new_dist_sq

        # Permanently add best center candidate found in local tries
        centers[c] = X[best_candidate]
        current_pot = best_pot
        closest_dist_sq = best_dist_sq

    return centers


###############################################################################
# K-means estimation by EM (expectation maximisation)

def k_means(X, k, init='k-means++', n_init=10, max_iter=300, verbose=0,
                    tol=1e-4, random_state=None, copy_x=True):
    """ K-means clustering algorithm.

    Parameters
    ----------
    X: ndarray
        A M by N array of M observations in N dimensions or a length
        M array of M one-dimensional observations.

    k: int or ndarray
        The number of clusters to form as well as the number of
        centroids to generate.

    max_iter: int, optional, default 300
        Maximum number of iterations of the k-means algorithm to run.

    n_init: int, optional, default: 10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of
        n_init consecutive runs in terms of inertia.

    init: {'k-means++', 'random', or ndarray, or a callable}, optional
        Method for initialization, default to 'k-means++':

        'k-means++' : selects initial cluster centers for k-mean
        clustering in a smart way to speed up convergence. See section
        Notes in k_init for more details.

        'random': generate k centroids from a Gaussian with mean and
        variance estimated from the data.

        If an ndarray is passed, it should be of shape (k, p) and gives
        the initial centers.

    tol: float, optional
        The relative increment in the results before declaring convergence.

    verbose: boolean, optional
        Terbosity mode

    random_state: numpy.RandomState, optional
        The generator used to initialize the centers. Defaults to numpy.random.

    copy_x: boolean, optional
        When pre-computing distances it is more numerically accurate to center
        the data first.  If copy_x is True, then the original data is not
        modified.  If False, the original data is modified, and put back before
        the function returns, but small numerical differences may be introduced
        by subtracting and then adding the data mean.

    Returns
    -------
    centroid: ndarray
        A k by N array of centroids found at the last iteration of
        k-means.

    label: ndarray
        label[i] is the code or index of the centroid the
        i'th observation is closest to.

    inertia: float
        The final value of the inertia criterion

    """
    random_state = check_random_state(random_state)
    n_samples = X.shape[0]

    vdata = np.mean(np.var(X, 0))
    best_inertia = np.infty
    if hasattr(init, '__array__'):
        init = np.asarray(init)
        if not n_init == 1:
            warnings.warn('Explicit initial center position passed: '
                          'performing only one init in the k-means')
            n_init = 1

    # subtract of mean of x for more accurate distance computations
    X_mean = X.mean(axis=0)
    if copy_x:
        X = X.copy()
    X -= X_mean

    # precompute squared norms of data points
    x_squared_norms = X.copy()
    x_squared_norms **= 2
    x_squared_norms = x_squared_norms.sum(axis=1)
    for it in range(n_init):
        # init
        centers = _init_centroids(X, k, init, random_state=random_state,
                                  x_squared_norms=x_squared_norms)
        if verbose:
            print 'Initialization complete'

        # iterations
        for i in range(max_iter):
            centers_old = centers.copy()
            labels, inertia = _e_step(X, centers,
                                        x_squared_norms=x_squared_norms)
            centers = _m_step(X, labels, k)

            if verbose:
                print 'Iteration %i, inertia %s' % (i, inertia)

            if np.sum((centers_old - centers) ** 2) < tol * vdata:
                if verbose:
                    print 'Converged to similar centers at iteration', i
                break

            if inertia < best_inertia:
                best_labels = labels.copy()
                best_centers = centers.copy()
                best_inertia = inertia

    else:
        best_labels = labels
        best_centers = centers
        best_inertia = inertia
    if not copy_x:
        X += X_mean
    return best_centers + X_mean, best_labels, best_inertia


def _calculate_labels_inertia(X, centers):
    """Compute the inertia and the labels of the given samples and centers"""
    norm = (X ** 2).sum(axis=1)
    distance = euclidean_distances(centers, X, norm, squared=True)
    return distance.min(axis=0).sum(), distance.argmin(axis=0)


def _mini_batch_step(X, centers, counts, x_squared_norms=None):
    """Incremental update of the centers for the Minibatch K-Means algorithm

    Parameters
    ----------

    X: array, shape (n_samples, n_features)

    centers: array, shape (k, n_features)
        The cluster centers

    i: int
         The iterator: it is used to calculate which section of the data to
         use for the computation of the new centers

    counts: array, shape (k, )
         The vector in which we keep track of the numbers of elements in a
         cluster

    x_squared_norms: array, shape (n_samples,)
        Squared euclidean norm of each data point.

    Returns
    -------
    centers: array, shape (k, n_features)
        The resulting centers

    """
    m_norm = (X ** 2).sum(axis=1)
    cache = euclidean_distances(centers, X, m_norm, squared=True).argmin(
        axis=0)

    k = centers.shape[0]
    for q in range(k):
        center_mask = (cache == q)
        c = center_mask.sum()
        if np.any(center_mask):
            centers[q] = (1. / (counts[q] + c)) * (
                counts[q] * centers[q] + np.sum(X[center_mask], axis=0))
            counts[q] += c

    return centers, counts


def _m_step(X, z, k):
    """M step of the K-means EM algorithm

    Computation of cluster centers/means

    Parameters
    ----------
    X: array, shape (n_samples, n_features)

    z: array, shape (n_samples)
        Current assignment

    k: int
        Number of desired clusters

    Returns
    -------
    centers: array, shape (k, n_features)
        The resulting centers
    """
    dim = X.shape[1]
    centers = np.empty((k, dim))
    X_center = None
    for q in range(k):
        center_mask = (z == q)
        if not np.any(center_mask):
            # The centroid of empty clusters is set to the center of
            # everything
            if X_center is None:
                X_center = X.mean(axis=0)
            centers[q] = X_center
        else:
            centers[q] = np.mean(X[center_mask], axis=0)
    return centers


def _init_centroids(X, k, init, random_state=None, x_squared_norms=None):
    """Compute the initial centroids

    Parameters
    ----------

    X: array, shape (n_samples, n_features)

    k: int
        number of centroids

    init: {'k-means++', 'random' or ndarray or callable} optional
        Method for initialisation

    random_state: numpy.RandomState, optional
        The generator used to initialise the centers. Defaults to numpy.random

    x_squared_norms:  array, shape (n_samples,), optional
        Squared euclidean norm of each data point. Pass it if you have it at
        hands already to avoid it being recomputed here. Default: None
    """
    random_state = check_random_state(random_state)


    n_samples = X.shape[0]
    if init == 'k-means++':
        centers = k_init(X, k, random_state=random_state, x_squared_norms=x_squared_norms)
    elif init == 'random':
        seeds = np.argsort(random_state.rand(n_samples))[:k]
        centers = X[seeds]
    elif hasattr(init, '__array__'):
        centers = np.asanyarray(init).copy()
    elif callable(init):
        centers = init(X, k, random_state=randome_state)
    else:
        raise ValueError("the init parameter for the k-means should "
            "be 'k-means++' or 'random' or an ndarray, "
            "'%s' (type '%s') was passed.")
    return centers


def _e_step(x, centers, precompute_distances=True, x_squared_norms=None):
    """E step of the K-means EM algorithm

    Computation of the input-to-cluster assignment

    Parameters
    ----------
    x: array, shape (n_samples, n_features)

    centers: array, shape (k, n_features)
        The cluster centers

    precompute_distances: bool, optional
        Whether to compute the full distance matrix between centers and data
        points at once for more speed at the cost of memory. Default: True

    x_squared_norms: array, shape (n_samples,), optional
        Squared euclidean norm of each data point, speeds up computations in
        case of precompute_distances == True. Default: None

    Returns
    -------
    z: array of shape(n)
        The resulting assignment

    inertia: float
        The value of the inertia criterion with the assignment
    """

    n_samples = x.shape[0]
    k = centers.shape[0]

    if precompute_distances:
        distances = euclidean_distances(centers, x, x_squared_norms,
                                        squared=True)
    z = np.empty(n_samples, dtype=np.int)
    z.fill(-1)
    mindist = np.empty(n_samples)
    mindist.fill(np.infty)
    for q in range(k):
        if precompute_distances:
            dist = distances[q]
        else:
            dist = np.sum((x - centers[q]) ** 2, axis=1)
        z[dist < mindist] = q
        mindist = np.minimum(dist, mindist)
    inertia = mindist.sum()
    return z, inertia


class KMeans(BaseEstimator):
    """K-Means clustering

    Parameters
    ----------

    k : int or ndarray
        The number of clusters to form as well as the number of
        centroids to generate.

    max_iter : int
        Maximum number of iterations of the k-means algorithm for a
        single run.

    n_init: int, optional, default: 10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of
        n_init consecutive runs in terms of inertia.

    init : {'k-means++', 'random' or an ndarray}
        Method for initialization, defaults to 'random':

        'k-means++' : selects initial cluster centers for k-mean
        clustering in a smart way to speed up convergence. See section
        Notes in k_init for more details.

        'random': choose k observations (rows) at random from data for
        the initial centroids.

        if init is an 2d array, it is used as a seed for the centroids

    tol: float, optional default: 1e-4
        Relative tolerance w.r.t. inertia to declare convergence

    Methods
    -------

    fit(X):
        Compute K-Means clustering

    Attributes
    ----------

    cluster_centers_: array, [n_clusters, n_features]
        Coordinates of cluster centers

    labels_:
        Labels of each point

    inertia_: float
        The value of the inertia criterion associated with the chosen
        partition.

    Notes
    ------

    The k-means problem is solved using the Lloyd algorithm.

    The average complexity is given by O(k n T), were n is the number of
    samples and T is the number of iteration.

    The worst case complexity is given by O(n^(k+2/p)) with
    n = n_samples, p = n_features. (D. Arthur and S. Vassilvitskii,
    'How slow is the k-means method?' SoCG2006)

    In practice, the K-means algorithm is very fast (one of the fastest
    clustering algorithms available), but it falls in local minima. That's why
    it can be useful to restart it several times.
    """

    def __init__(self, k=8, init='random', n_init=10, max_iter=300, tol=1e-4,
            verbose=0, random_state=None, copy_x=True):
        self.k = k
        self.init = init
        self.max_iter = max_iter
        self.tol = tol
        self.n_init = n_init
        self.verbose = verbose
        self.random_state = random_state
        self.copy_x = copy_x

    def _check_data(self, X, **params):
        """
        Set parameters and check the sample given is larger than k
        """
        X = np.asarray(X)
 
        X = np.asanyarray(X)
        if X.shape[0] < self.k:
            raise ValueError("n_samples=%d should be larger than k=%d" % (
                X.shape[0], self.k))
        self._set_params(**params)
        return X

    def fit(self, X, **params):
        """Compute k-means"""

        self.random_state = check_random_state(self.random_state)

        X = self._check_data(X, **params)

        self.cluster_centers_, self.labels_, self.inertia_ = k_means(
            X, k=self.k, init=self.init, n_init=self.n_init,
            max_iter=self.max_iter, verbose=self.verbose,
            tol=self.tol, random_state=self.random_state, copy_x=self.copy_x)
        return self


class MiniBatchKMeans(KMeans):
    """
    Batch K-Means clustering

    Parameters
    ----------

    k : int or ndarray
        The number of clusters to form as well as the number of
        centroids to generate. If init initialization string is
        'matrix', or if a ndarray is given instead, it is
        interpreted as initial cluster to use instead.

    max_iter : int
        Maximum number of iterations of the k-means algorithm for a
        single run.

    n_init: int, optional, default: 10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of
        n_init consecutive runs in terms of inertia.

    init : {'k-means++', 'random' or an ndarray}
        Method for initialization, defaults to 'random':

        'k-means++' : selects initial cluster centers for k-mean
        clustering in a smart way to speed up convergence. See section
        Notes in k_init for more details.

        'random': choose k observations (rows) at random from data for
        the initial centroids.

        if init is an 2d array, it is used as a seed for the centroids

    tol: float, optional default: 1e-4
        Relative tolerance w.r.t. inertia to declare convergence

    Methods
    -------

    fit(X):
        Compute K-Means clustering

    partial_fit(X):
        Compute a partial K-Means clustering

    Attributes
    ----------

    cluster_centers_: array, [n_clusters, n_features]
        Coordinates of cluster centers

    labels_:
        Labels of each point

    inertia_: float
        The value of the inertia criterion associated with the chosen
        partition.

    Notes
    ------

    The batch k-means problem is solved using the Lloyd algorithm.

    http://www.eecs.tufts.edu/~dsculley/papers/fastkmeans.pdf

    """

    def __init__(self, k=8, init='random', n_init=10,
                 verbose=0, random_state=None, copy_x=True):
        super(MiniBatchKMeans, self).__init__(k, init, n_init,
              verbose, random_state=None, copy_x=True)
        # FIXME
        # counts is an array used to keep track of who went where
        self.counts = None
        self.cluster_centers = None

    def partial_fit(self, X, y=None, **params):
        """Update k means estimate on a single mini-batch X"""

        self.random_state = check_random_state(self.random_state)

        if hasattr(self.init, '__array__'):
            X = self._check_data(X, **params)
            self.init = np.asarray(self.init)

        if len(X) == 0:
            return self
        x_squared_norms = X.copy()
        x_squared_norms **= 2
        x_squared_norms = x_squared_norms.sum(axis=1)

        if self.counts is None:
            # this is the first call partial_fit on this object:
            # initialize the cluster centers
            self.cluster_centers = _init_centroids(
                X, self.k, self.init, random_state=self.random_state,
                x_squared_norms=x_squared_norms)

            self.counts = np.zeros(self.k)

        self.cluster_centers, self.counts = _mini_batch_step(
            X, self.cluster_centers, self.counts,
            x_squared_norms=x_squared_norms)

        self.inertia_, self.labels_ = _calculate_labels_inertia(
            X, self.cluster_centers)

        return self
