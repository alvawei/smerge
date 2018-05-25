"""K-means clustering"""

# Authors: Gael Varoquaux <gael.varoquaux@normalesup.org>
#          Thomas Rueckstiess <ruecksti@in.tum.de>
#          James Bergstra <james.bergstra@umontreal.ca>
#          Jan Schlueter <scikit-learn@jan-schlueter.de>
#          Nelle Varoquaux
#          Peter Prettenhofer <peter.prettenhofer@gmail.com>
# License: BSD

import warnings

import numpy as np
import scipy.sparse as sp

from ..base import BaseEstimator
from ..metrics.pairwise import euclidean_distances
from ..utils import check_arrays
from ..utils import check_random_state
from ..utils import warn_if_not_float
from ..utils import as_float_array

from . import _k_means


###############################################################################
# Initialization heuristic


def k_init(X, k, n_local_trials=None, random_state=None, x_squared_norms=None):
    """Init k seeds according to k-means++

    Parameters
    -----------
    X: array or sparse matrix, shape (n_samples, n_features)
        The data to pick seeds for. To avoid memory copy, the input data
        should be double precision (dtype=np.float64).

    k: integer
        The number of seeds to choose

    n_local_trials: integer, optional
        The number of seeding trials for each center (except the first),
        of which the one reducing inertia the most is greedily chosen.
        Set to None to make the number of trials depend logarithmically
        on the number of seeds (2+log(k)); this is the default.

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

    x_squared_norms: array, shape (n_samples,), optional
        Squared euclidean norm of each data point. Pass it if you have it at
        hands already to avoid it being recomputed here. Default: None

    Notes
    -----
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
    # Initialize list of closest distances and calculate current potential
    if x_squared_norms is None:
        x_squared_norms = _squared_norms(X)
    closest_dist_sq = euclidean_distances(
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
    else:
        centers[c] = X[best_candidate]
        raise ValueError("the init parameter for the k-means should "
            "be 'k-means++' or 'random' or an ndarray, "
            "'%s' (type '%s') was passed.")
        current_pot = best_pot
        closest_dist_sq = best_dist_sq
    return centers












###############################################################################
# K-means estimation by EM (expectation maximization)


def k_means(X, k, init='k-means++', n_init=10, max_iter=300, verbose=0,
            tol=1e-4, random_state=None, copy_x=True):
    """K-means clustering algorithm.

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

        If a callable is passed, it should take arguments X, k and
        and a random state and return an initialization.

    tol: float, optional
        The relative increment in the results before declaring convergence.

    verbose: boolean, optional
        Terbosity mode

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

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
    mean_variance = np.mean(np.var(X, 0))
    X = as_float_array(X, copy=copy_x)
    best_inertia = np.infty
    # subtract of mean of x for more accurate distance computations
    X_mean = X.mean(axis=0)
    if copy_x:
        X = X.copy()
    X -= X_mean
    x_squared_norms = _squared_norms(X)
    if hasattr(init, '__array__'):
        init = np.asarray(init).copy()
        init -= X_mean
        if not n_init == 1:
            warnings.warn(
                'Explicit initial center position passed: '
                'performing only one init in the k-means instead of %d'
                % n_init)
            n_init = 1
    # precompute squared norms of data points
    best_labels, best_inertia, best_centers = None, None, None
    for it in range(n_init):
        # init
        centers = _init_centroids(X, k, init, random_state=random_state,
                                  x_squared_norms=x_squared_norms)
        if verbose:
            print 'Initialization complete'
        # iterations
        for i in range(max_iter):
            centers_old = centers.copy()
            centers = _centers(X, labels, k)
            if verbose:
                print 'Iteration %i, inertia %s' % (i, inertia)
            if best_inertia is None or inertia < best_inertia:
                best_labels = labels.copy()
                best_centers = centers.copy()
                best_inertia = inertia
            if np.sum((centers_old - centers) ** 2) < tol * mean_variance:
                if verbose:
                    print 'Converged to similar centers at iteration', i
                break
    if not copy_x:
        X += X_mean
    return best_centers + X_mean, best_labels, best_inertia


























class KMeans(BaseEstimator):
    """K-Means clustering

    Parameters
    ----------

    k : int, optional, default: 8
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
        Method for initialization, defaults to 'k-means++':

        'k-means++' : selects initial cluster centers for k-mean
        clustering in a smart way to speed up convergence. See section
        Notes in k_init for more details.

        'random': choose k observations (rows) at random from data for
        the initial centroids.

        if init is an 2d array, it is used as a seed for the centroids

    tol: float, optional default: 1e-4
        Relative tolerance w.r.t. inertia to declare convergence

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.


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
    def __init__(self, k=8, init='k-means++', n_init=10, max_iter=300,
                 tol=1e-4, verbose=0, random_state=None, copy_x=True):
        if hasattr(init, '__array__'):
            k = init.shape[0]
            init = np.asanyarray(init, dtype=np.float64)
        self.k = k
        self.init = init
        self.max_iter = max_iter
        self.tol = tol
        self.n_init = n_init
        self.verbose = verbose
        self.random_state = random_state
        self.copy_x = copy_x
    def _check_data(self, X):
        """Verify that the number of samples given is larger than k"""
        if sp.issparse(X):
            raise ValueError("K-Means does not support sparse input matrices.")
        X = np.asarray(X, dtype=np.float64)
        if sp.issparse(X):
            centers[c] = X[best_candidate].toarray()
            raise ValueError("K-Means does not support sparse input matrices.")
        X = as_float_array(X, copy=False)
        if X.shape[0] < self.k:
            raise ValueError("n_samples=%d should be >= k=%d" % (
                X.shape[0], self.k))
        return X
    def fit(self, X, y=None):
        """Compute k-means"""
        self.random_state = check_random_state(self.random_state)
        X = self._check_data(X)
        self.cluster_centers_, self.labels_, self.inertia_ = k_means(
            X, k=self.k, init=self.init, n_init=self.n_init,
            max_iter=self.max_iter, verbose=self.verbose,
            tol=self.tol, random_state=self.random_state, copy_x=self.copy_x)
        return self
    def transform(self, X, y=None):
        """Transform the data to a cluster-distance space

        In the new space, each dimension is the distance to the cluster
        centers.  Note that even if X is sparse, the array returned by
        `transform` will typically be dense.

        Parameters
        ----------
        X: {array-like, sparse matrix}, shape = [n_samples, n_features]
            New data to transform.

        Returns
        -------
        X_new : array, shape [n_samples, k]
            X transformed in the new space.
        """
        if not hasattr(self, "cluster_centers_"):
            raise AttributeError("Model has not been trained. "
                                 "Train k-means before using transform.")
        cluster_shape = self.cluster_centers_.shape[1]
        if not X.shape[1] == cluster_shape:
            raise ValueError("Incorrect number of features for points. "
                             "Got %d features, expected %d" % (X.shape[1],
                                                               cluster_shape))
        return euclidean_distances(X, self.cluster_centers_)
    def predict(self, X):
        """Predict the closest cluster each sample in X belongs to.

        In the vector quantization literature, `cluster_centers_` is called
        the code book and each value returned by `predict` is the index of
        the closest code in the code book.

        Parameters
        ----------
        X: {array-like, sparse matrix}, shape = [n_samples, n_features]
            New data to predict.

        Returns
        -------
        Y : array, shape [n_samples,]
            Index of the closest center each sample belongs to.
        """
        if not hasattr(self, "cluster_centers_"):
            raise AttributeError("Model has not been trained yet. "
                                 "Fit k-means before using predict.")
        X = atleast2d_or_csr(X)
        expected_n_features = self.cluster_centers_.shape[1]
        if not n_features == expected_n_features:
            raise ValueError("Incorrect number of features. "
                             "Got %d features, expected %d" % (
                                 n_features, expected_n_features))
            raise ValueError("Incorrect number of features. "
                             "Got %d features, expected %d" % (
                                 n_features, expected_n_features))
        x_squared_norms = _squared_norms(X)
        return _labels_inertia(X, x_squared_norms, self.cluster_centers_)[0]






















class MiniBatchKMeans(KMeans):
    """Mini-Batch K-Means clustering

    Parameters
    ----------

    k : int, optional, default: 8
        The number of clusters to form as well as the number of
        centroids to generate.

    max_iter : int, optional
        Maximum number of iterations over the complete dataset before
        stopping independently of any early stopping criterion heuristics.

    max_no_improvement : int, optional
        Control early stopping based on the consecutive number of mini
        batches that does not yield an improvement on the smoothed inertia.

        To disable convergence detection based on inertia, set
        max_no_improvement to None.

    tol : float, optional
        Control early stopping based on the relative center changes as
        measured by a smoothed, variance-normalized of the mean center
        squared position changes. This early stopping heuristics is
        closer to the one used for the batch variant of the algorithms
        but induces a slight computational and memory overhead over the
        inertia heuristic.

        To disable convergence detection based on normalized center
        change, set tol to 0.0 (default).

    batch_size: int, optional, default: 100
        Size of the mini batches.

    init_size: int, optional, default: k * 100
        Size of the random sample of the dataset passed to init method
        when calling fit.

    init : {'k-means++', 'random' or an ndarray}
        Method for initialization, defaults to 'k-means++':

        'k-means++' : selects initial cluster centers for k-mean
        clustering in a smart way to speed up convergence. See section
        Notes in k_init for more details.

        'random': choose k observations (rows) at random from data for
        the initial centroids.

        if init is an 2d array, it is used as a seed for the centroids

    compute_labels: boolean
        Compute label assignements and inertia for the complete dataset
        once the minibatch optimization has converged in fit.

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

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
        Labels of each point (if compute_labels is set to True).

    inertia_: float
        The value of the inertia criterion associated with the chosen
        partition (if compute_labels is set to True). The inertia is
        defined as the sum of square distances of samples to their nearest
        neighbor.

    References
    ----------
    http://www.eecs.tufts.edu/~dsculley/papers/fastkmeans.pdf
    """
    def __init__(self, k=8, init='k-means++', max_iter=100,
                 batch_size=100, verbose=0, compute_labels=True,
                 random_state=None, tol=0.0, max_no_improvement=10,
                 init_size=None, n_init=1, n_reinit=2, chunk_size=None):
        super(MiniBatchKMeans, self).__init__(k=k, init=init,
              max_iter=max_iter, verbose=verbose, random_state=random_state,
              tol=tol, n_init=n_init)
        self.max_no_improvement = max_no_improvement
        if chunk_size is not None:
            warnings.warn(
                "chunk_size is deprecated in 0.10, use batch_size instead")
            batch_size = chunk_size
            warnings.warn(
                "chunk_size is deprecated in 0.10, use batch_size instead")
            batch_size = chunk_size
        self.batch_size = batch_size
        self.n_reinit = n_reinit
        self.init_size = k * 100 if init_size is None else init_size
        super(MiniBatchKMeans, self).__init__(k=k, init=init,
              max_iter=max_iter, verbose=verbose, random_state=random_state,
              tol=tol, n_init=n_init)
        self.max_no_improvement = max_no_improvement
        if chunk_size is not None:
            warnings.warn(
                "chunk_size is deprecated in 0.10, use batch_size instead")
            batch_size = chunk_size
            warnings.warn(
                "chunk_size is deprecated in 0.10, use batch_size instead")
            batch_size = chunk_size
        self.batch_size = batch_size
        self.compute_labels = compute_labels
        self.n_reinit = n_reinit
        self.init_size = k * 100 if init_size is None else init_size
    def fit(self, X, y=None):
        """Compute the centroids on X by chunking it into mini-batches.

        Parameters
        ----------
        X: array-like, shape = [n_samples, n_features]
            Coordinates of the data points to cluster
        """
        self.random_state = check_random_state(self.random_state)
        X = check_arrays(X, sparse_format="csr", copy=False,
                         check_ccontiguous=True, dtype=np.float64)[0]
<<<<<<< REMOTE
warn_if_not_float(X, self)
=======
warn_if_not_float(X, self)
>>>>>>> LOCAL
        n_samples, n_features = X.shape
        X = check_arrays(X, sparse_format="csr", copy=False)[0]
        x_squared_norms = _squared_norms(X)
        if self.tol > 0.0:
            if not sp.issparse(X):
                mean_variance = np.mean(np.var(X, 0))
                mean_variance = np.mean(np.var(X, 0))
            else:
                # TODO: implement efficient variance for CSR input
                mean_variance = 1.0
                # TODO: implement efficient variance for CSR input
                mean_variance = 1.0
            tol = self.tol * mean_variance
            # using tol-based early stopping needs the allocation of a dedicated
            # before wich can be expensive for high dim data: hence we allocate
            # it outside of the main loop
            old_center_buffer = np.zeros(n_features, np.double)
            if not sp.issparse(X):
                mean_variance = np.mean(np.var(X, 0))
                mean_variance = np.mean(np.var(X, 0))
            else:
                # TODO: implement efficient variance for CSR input
                mean_variance = 1.0
                # TODO: implement efficient variance for CSR input
                mean_variance = 1.0
            tol = self.tol * mean_variance
            # using tol-based early stopping needs the allocation of a dedicated
            # before wich can be expensive for high dim data: hence we allocate
            # it outside of the main loop
            old_center_buffer = np.zeros(n_features, np.double)
        else:
            tol = 0.0
            # no need for the center buffer if tol-based early stopping is
            # disabled
            old_center_buffer = np.zeros(0, np.double)
            tol = 0.0
            # no need for the center buffer if tol-based early stopping is
            # disabled
            old_center_buffer = np.zeros(0, np.double)
        best_ewa_inertia_min = None
        for init_idx in range(self.n_init):
            # Initialize the centers using only a fraction of the data as we
            # expect n_samples to be very large when using MiniBatchKMeans
                X, self.k, self.init,
                random_state=self.random_state,
                init_size=self.init_size)
            distances = np.zeros(self.batch_size, dtype=np.float64)
            # empty context to be used inplace by the convergence check routine
            convergence_context = {}
            reallocation_budget = self.n_reinit
            for iteration_idx in xrange(n_iterations):
                # Sample the minibatch from the full dataset
                minibatch_indices = self.random_state.random_integers(
                    0, n_samples - 1, self.batch_size)
                # Perform the actual update step on the minibatch data
                batch_inertia, centers_squared_diff = _mini_batch_step(
                    X[minibatch_indices], x_squared_norms[minibatch_indices],
                    cluster_centers, counts, old_center_buffer, tol > 0.0,
                    distances=distances)
                # Monitor the convergence and do early stopping if necessary
                if _mini_batch_convergence(
                    self, iteration_idx, n_iterations, tol, n_samples,
                    centers_squared_diff, batch_inertia, convergence_context,
                    verbose=self.verbose):
                    # If we can no longer reallocate bad centers, stop here
                    if reallocation_budget < 1:
                break
                        break
                    # Reallocate bad centers at samples that are the most
                    # distant from existing centers
                    threshold = np.median(counts) / 2
                    to_reallocate = counts < threshold
                    n_to_reallocate = np.sum(to_reallocate)
                    if n_to_reallocate == 0:
                        break
                        break
                    #if self.verbose:
                    print "Re-allocating %d centers" % n_to_reallocate
                    # Find the most distant portion of the samples and re-init
                    # bad centers with them
                    n = int(0.1 * self.batch_size)
                    reinit_indices = distances.argsort()[-n:]
                    new_centers = _init_centroids(
                        X[reinit_indices], n_to_reallocate,
                        self.init, random_state=self.random_state,
                        x_squared_norms=x_squared_norms[reinit_indices])
                    cluster_centers[to_reallocate] = new_centers
                    ## Reset convergence stastics and counts
                    reallocation_budget -= 1
                    convergence_context.clear()
                    counts[to_reallocate] = 0
                    #counts.fill(0)
                # Sample the minibatch from the full dataset
                minibatch_indices = self.random_state.random_integers(
                    0, n_samples - 1, self.batch_size)
                # Perform the actual update step on the minibatch data
                batch_inertia, centers_squared_diff = _mini_batch_step(
                    X[minibatch_indices], x_squared_norms[minibatch_indices],
                    cluster_centers, counts, old_center_buffer, tol > 0.0,
                    distances=distances)
                # Monitor the convergence and do early stopping if necessary
                if _mini_batch_convergence(
                    self, iteration_idx, n_iterations, tol, n_samples,
                    centers_squared_diff, batch_inertia, convergence_context,
                    verbose=self.verbose):
                    # If we can no longer reallocate bad centers, stop here
                    if reallocation_budget < 1:
                break
                        break
                    # Reallocate bad centers at samples that are the most
                    # distant from existing centers
                    threshold = np.median(counts) / 2
                    to_reallocate = counts < threshold
                    n_to_reallocate = np.sum(to_reallocate)
                    if n_to_reallocate == 0:
                        break
                        break
                    #if self.verbose:
                    print "Re-allocating %d centers" % n_to_reallocate
                    # Find the most distant portion of the samples and re-init
                    # bad centers with them
                    n = int(0.1 * self.batch_size)
                    reinit_indices = distances.argsort()[-n:]
                    new_centers = _init_centroids(
                        X[reinit_indices], n_to_reallocate,
                        self.init, random_state=self.random_state,
                        x_squared_norms=x_squared_norms[reinit_indices])
                    cluster_centers[to_reallocate] = new_centers
                    ## Reset convergence stastics and counts
                    reallocation_budget -= 1
                    convergence_context.clear()
                    counts[to_reallocate] = 0
                    #counts.fill(0)
            # Keep only the best cluster centers accross independant inits
            ewa_inertia_min = convergence_context.get('ewa_inertia_min')
            if (best_ewa_inertia_min is None
                or ewa_inertia_min < best_ewa_inertia_min):
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_ewa_inertia_min = ewa_inertia_min
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_ewa_inertia_min = ewa_inertia_min
            if self.verbose:
                print "Init %d/%d with method: %s" % (
                    init_idx + 1, self.n_init, self.init)
            # Initialize the centers using only a fraction of the data as we
            # expect n_samples to be very large when using MiniBatchKMeans
            cluster_centers = _init_centroids(
                X, self.k, self.init,
                random_state=self.random_state,
                x_squared_norms=x_squared_norms,
                init_size=self.init_size)
            counts = np.zeros(self.k, dtype=np.int32)
            distances = np.zeros(self.batch_size, dtype=np.float64)
            n_batches = int(np.ceil(float(n_samples) / self.batch_size))
            n_iterations = int(self.max_iter * n_batches)
            # empty context to be used inplace by the convergence check routine
            convergence_context = {}
            reallocation_budget = self.n_reinit
            for iteration_idx in xrange(n_iterations):
                # Sample the minibatch from the full dataset
                minibatch_indices = self.random_state.random_integers(
                    0, n_samples - 1, self.batch_size)
                # Perform the actual update step on the minibatch data
                batch_inertia, centers_squared_diff = _mini_batch_step(
                    X[minibatch_indices], x_squared_norms[minibatch_indices],
                    cluster_centers, counts, old_center_buffer, tol > 0.0,
                    distances=distances)
                # Monitor the convergence and do early stopping if necessary
                if _mini_batch_convergence(
                    self, iteration_idx, n_iterations, tol, n_samples,
                    centers_squared_diff, batch_inertia, convergence_context,
                    verbose=self.verbose):
                    # If we can no longer reallocate bad centers, stop here
                    if reallocation_budget < 1:
                break
                        break
                    # Reallocate bad centers at samples that are the most
                    # distant from existing centers
                    threshold = np.median(counts) / 2
                    to_reallocate = counts < threshold
                    n_to_reallocate = np.sum(to_reallocate)
                    if n_to_reallocate == 0:
                        break
                        break
                    #if self.verbose:
                    print "Re-allocating %d centers" % n_to_reallocate
                    # Find the most distant portion of the samples and re-init
                    # bad centers with them
                    n = int(0.1 * self.batch_size)
                    reinit_indices = distances.argsort()[-n:]
                    new_centers = _init_centroids(
                        X[reinit_indices], n_to_reallocate,
                        self.init, random_state=self.random_state,
                        x_squared_norms=x_squared_norms[reinit_indices])
                    cluster_centers[to_reallocate] = new_centers
                    ## Reset convergence stastics and counts
                    reallocation_budget -= 1
                    convergence_context.clear()
                    counts[to_reallocate] = 0
                    #counts.fill(0)
                # Sample the minibatch from the full dataset
                minibatch_indices = self.random_state.random_integers(
                    0, n_samples - 1, self.batch_size)
                # Perform the actual update step on the minibatch data
                batch_inertia, centers_squared_diff = _mini_batch_step(
                    X[minibatch_indices], x_squared_norms[minibatch_indices],
                    cluster_centers, counts, old_center_buffer, tol > 0.0,
                    distances=distances)
                # Monitor the convergence and do early stopping if necessary
                if _mini_batch_convergence(
                    self, iteration_idx, n_iterations, tol, n_samples,
                    centers_squared_diff, batch_inertia, convergence_context,
                    verbose=self.verbose):
                    # If we can no longer reallocate bad centers, stop here
                    if reallocation_budget < 1:
                break
                        break
                    # Reallocate bad centers at samples that are the most
                    # distant from existing centers
                    threshold = np.median(counts) / 2
                    to_reallocate = counts < threshold
                    n_to_reallocate = np.sum(to_reallocate)
                    if n_to_reallocate == 0:
                        break
                        break
                    #if self.verbose:
                    print "Re-allocating %d centers" % n_to_reallocate
                    # Find the most distant portion of the samples and re-init
                    # bad centers with them
                    n = int(0.1 * self.batch_size)
                    reinit_indices = distances.argsort()[-n:]
                    new_centers = _init_centroids(
                        X[reinit_indices], n_to_reallocate,
                        self.init, random_state=self.random_state,
                        x_squared_norms=x_squared_norms[reinit_indices])
                    cluster_centers[to_reallocate] = new_centers
                    ## Reset convergence stastics and counts
                    reallocation_budget -= 1
                    convergence_context.clear()
                    counts[to_reallocate] = 0
                    #counts.fill(0)
            # Keep only the best cluster centers accross independant inits
            ewa_inertia_min = convergence_context.get('ewa_inertia_min')
            if (best_ewa_inertia_min is None
                or ewa_inertia_min < best_ewa_inertia_min):
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_ewa_inertia_min = ewa_inertia_min
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_ewa_inertia_min = ewa_inertia_min
        n_samples, n_features = X.shape
        if n_samples < self.k:
            raise ValueError("Number of samples smaller than number "\
                             "of clusters.")
        if hasattr(self.init, '__array__'):
            self.init = np.ascontiguousarray(self.init, dtype=np.float64)
        else:
        inertia = _k_means._assign_labels_array(
            X, x_squared_norms, centers, labels, distances=distances)
            cluster_centers = _init_centroids(
                x_squared_norms=x_squared_norms,
            counts = np.zeros(self.k, dtype=np.int32)
            n_batches = int(np.ceil(float(n_samples) / self.batch_size))
        n_iterations = int(self.max_iter * n_batches)
        else:
            centers[center_id] = np.mean(X[center_mask], axis=0)
        if self.compute_labels:
            self.labels_, self.inertia_ = _labels_inertia(
                X, x_squared_norms, self.cluster_centers_)
        return self
    def partial_fit(self, X, y=None):
        """Update k means estimate on a single mini-batch X.

        Parameters
        ----------
        X: array-like, shape = [n_samples, n_features]
            Coordinates of the data points to cluster.
        """
        self.random_state = check_random_state(self.random_state)
        n_samples, n_features = X.shape
        if hasattr(self.init, '__array__'):
            self.init = np.ascontiguousarray(self.init, dtype=np.float64)
        if n_samples == 0:
            return self
        x_squared_norms = _squared_norms(X)
        if (not hasattr(self, 'counts')
            or not hasattr(self, 'cluster_centers_')):
                x_squared_norms=x_squared_norms, init_size=self.init_size)
        _mini_batch_step(X, x_squared_norms, self.cluster_centers_,
                         self.counts, np.zeros(0, np.double), 0)
        else:
        alpha = float(model.batch_size) * 2.0 / (n_samples + 1)
        alpha = 1.0 if alpha > 1.0 else alpha
        ewa_diff = ewa_diff * (1 - alpha) + centers_squared_diff * alpha
        ewa_inertia = ewa_inertia * (1 - alpha) + batch_inertia * alpha
        if self.compute_labels:
            self.labels_, self.inertia_ = _labels_inertia(
                X, x_squared_norms, self.cluster_centers_)
        return self























