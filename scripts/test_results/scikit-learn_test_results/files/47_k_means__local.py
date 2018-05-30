"""K-means clustering"""

# Authors: Gael Varoquaux <gael.varoquaux@normalesup.org>
#          Thomas Rueckstiess <ruecksti@in.tum.de>
#          James Bergstra <james.bergstra@umontreal.ca>
#          Jan Schlueter <scikit-learn@jan-schlueter.de>
#          Nelle Varoquaux
#          Peter Prettenhofer <peter.prettenhofer@gmail.com>
#          Olivier Grisel <olivier.grisel@ensta.org>
# License: BSD

import warnings

import numpy as np
import scipy.sparse as sp

from ..base import BaseEstimator
from ..metrics.pairwise import euclidean_distances
from ..utils.sparsefuncs import mean_variance_axis0
from ..utils import check_arrays
from ..utils import check_random_state
from ..utils import atleast2d_or_csr
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
    if sp.issparse(X):
        centers[0] = X[center_id].toarray()
    else:
        centers[0] = X[center_id]

    # Initialize list of closest distances and calculate current potential
    if x_squared_norms is None:
        x_squared_norms = _squared_norms(X)
    closest_dist_sq = euclidean_distances(
        centers[0], X, Y_norm_squared=x_squared_norms, squared=True)
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
        if sp.issparse(X):
            centers[c] = X[best_candidate].toarray()
        else:
            centers[c] = X[best_candidate]
        current_pot = best_pot
        closest_dist_sq = best_dist_sq

    return centers


###############################################################################
# K-means batch estimation by EM (expectation maximization)


def k_means(X, k, init='k-means++', precompute_distances=True,
            n_init=10, max_iter=300, verbose=0,
            tol=1e-4, random_state=None, copy_x=True):
    """K-means clustering algorithm.

    Parameters
    ----------
    X: array-like of floats, shape (n_samples, n_features)
        The observations to cluster.

    k: int
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
    centroid: float ndarray with shape (k, n_features)
        Centroids found at the last iteration of k-means.

    label: integer ndarray with shape (n_samples,)
        label[i] is the code or index of the centroid the
        i'th observation is closest to.

    inertia: float
        The final value of the inertia criterion (sum of squared distances to
        the closest centroid for all observations in the training set).

    """
    random_state = check_random_state(random_state)

    mean_variance = np.mean(np.var(X, 0))
    best_inertia = np.infty
    X = as_float_array(X, copy=copy_x)

    # subtract of mean of x for more accurate distance computations
    X_mean = X.mean(axis=0)
    if copy_x:
        X = X.copy()
    X -= X_mean

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
    x_squared_norms = _squared_norms(X)

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
            # labels assignement is also called the E-step of EM
            labels, inertia = _labels_inertia(X, x_squared_norms, centers,
                                              precompute_distances)

            # computation of the means is also called the M-step of EM
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


def _squared_norms(X):
    """Compute the squared euclidean norms of the rows of X"""
    if sp.issparse(X):
        return _k_means.csr_row_norm_l2(X, squared=True)
    else:
        # TODO: implement a cython version to avoid the memory copy of the
        # input data
        return (X ** 2).sum(axis=1)


def _labels_inertia_precompute_dense(X, x_squared_norms, centers):
    n_samples = X.shape[0]
    k = centers.shape[0]
    distances = euclidean_distances(centers, X, x_squared_norms,
                                    squared=True)
    labels = np.empty(n_samples, dtype=np.int)
    labels.fill(-1)
    mindist = np.empty(n_samples)
    mindist.fill(np.infty)
    for center_id in range(k):
        dist = distances[center_id]
        labels[dist < mindist] = center_id
        mindist = np.minimum(dist, mindist)
    inertia = mindist.sum()
    return labels, inertia


def _labels_inertia(X, x_squared_norms, centers,
                    precompute_distances=True, distances=None):
    """E step of the K-means EM algorithm

    Compute the labels and the inertia of the given samples and centers

    Parameters
    ----------
    X: float64 array-like or CSR sparse matrix, shape (n_samples, n_features)
        The input samples to assign to the labels.

    x_squared_norms: array, shape (n_samples,)
        Precomputed squared euclidean norm of each data point, to speed up
        computations.

    centers: float64 array, shape (k, n_features)
        The cluster centers.

    distances: float64 array, shape (k, n_samples)
        Distances for each sample to its closest center.

    Returns
    -------
    labels: int array of shape(n)
        The resulting assignment

    inertia: float
        The value of the inertia criterion with the assignment
    """
    n_samples = X.shape[0]
    # set the default value of centers to -1 to be able to detect any anomaly
    # easily
    labels = - np.ones(n_samples, np.int32)
    if distances == None:
        distances = np.zeros(shape=(0,), dtype=np.float64)
    if sp.issparse(X):
        inertia = _k_means._assign_labels_csr(
            X, x_squared_norms, centers, labels, distances=distances)
    else:
        if precompute_distances:
            return _labels_inertia_precompute_dense(X, x_squared_norms,
                                                    centers)
        inertia = _k_means._assign_labels_array(
            X, x_squared_norms, centers, labels, distances=distances)
    return labels, inertia


def _centers(X, labels, n_clusters):
    """M step of the K-means EM algorithm

    Computation of cluster centers / means.

    Parameters
    ----------
    X: array, shape (n_samples, n_features)

    labels: array of integers, shape (n_samples)
        Current label assignment

    n_clusters: int
        Number of desired clusters

    Returns
    -------
    centers: array, shape (n_clusters, n_features)
        The resulting centers
    """
    # TODO: add support for CSR input
    n_features = X.shape[1]

    # TODO: explicit dtype handling
    centers = np.empty((n_clusters, n_features))
    X_center = None
    for center_id in range(n_clusters):
        center_mask = labels == center_id
        if not np.any(center_mask):
            # The centroid of empty clusters is set to the center of
            # everything
            if X_center is None:
                X_center = X.mean(axis=0)
            centers[center_id] = X_center
        else:
            centers[center_id] = np.mean(X[center_mask], axis=0)
    return centers


def _init_centroids(X, k, init, random_state=None, x_squared_norms=None,
                    init_size=None):
    """Compute the initial centroids

    Parameters
    ----------

    X: array, shape (n_samples, n_features)

    k: int
        number of centroids

    init: {'k-means++', 'random' or ndarray or callable} optional
        Method for initialization

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

    x_squared_norms:  array, shape (n_samples,), optional
        Squared euclidean norm of each data point. Pass it if you have it at
        hands already to avoid it being recomputed here. Default: None

    init_size : int, optional
        Number of samples to randomly sample for speeding up the
        initialization (sometimes at the expense of accurracy).

    Returns
    -------
    centers: array, shape(k, n_features)
    """
    random_state = check_random_state(random_state)
    n_samples = X.shape[0]

    if init_size is not None and init_size < n_samples:
        init_indices = random_state.random_integers(
                0, n_samples - 1, init_size)
        X = X[init_indices]
        x_squared_norms = x_squared_norms[init_indices]
        n_samples = X.shape[0]

    if init == 'k-means++':
        centers = k_init(X, k,
                        random_state=random_state,
                        x_squared_norms=x_squared_norms)
    elif init == 'random':
        seeds = random_state.permutation(n_samples)[:k]
        centers = X[seeds]
    elif hasattr(init, '__array__'):
        centers = init
    elif callable(init):
        centers = init(X, k, random_state=random_state)
    else:
        raise ValueError("the init parameter for the k-means should "
            "be 'k-means++' or 'random' or an ndarray, "
            "'%s' (type '%s') was passed.")

    if sp.issparse(centers):
        centers = centers.toarray()
    return centers


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

    precompute_distances : boolean
        Precompute distances (faster but takes more memory).

    tol: float, optional default: 1e-4
        Relative tolerance w.r.t. inertia to declare convergence

    random_state: integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

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
    The k-means problem is solved using Lloyd's algorithm.

    The average complexity is given by O(k n T), were n is the number of
    samples and T is the number of iteration.

    The worst case complexity is given by O(n^(k+2/p)) with
    n = n_samples, p = n_features. (D. Arthur and S. Vassilvitskii,
    'How slow is the k-means method?' SoCG2006)

    In practice, the k-means algorithm is very fast (one of the fastest
    clustering algorithms available), but it falls in local minima. That's why
    it can be useful to restart it several times.

    See also
    --------

    MiniBatchKMeans:
        Alternative online implementation that does incremental updates
        of the centers positions using mini-batches.
        For large scale learning (say n_samples > 10k) MiniBatchKMeans is
        probably much faster to than the default batch implementation.

    """

    def __init__(self, k=8, init='k-means++', n_init=10, max_iter=300,
                 tol=1e-4, precompute_distances=True,
                 verbose=0, random_state=None, copy_x=True):

        if hasattr(init, '__array__'):
            k = init.shape[0]
            init = np.asanyarray(init, dtype=np.float64)

        self.k = k
        self.init = init
        self.max_iter = max_iter
        self.tol = tol
        self.precompute_distances = precompute_distances
        self.n_init = n_init
        self.verbose = verbose
        self.random_state = random_state
        self.copy_x = copy_x

    def _check_fit_data(self, X):
        """Verify that the number of samples given is larger than k"""
        if sp.issparse(X):
            raise ValueError("K-Means does not support sparse input matrices.")
        X = np.asarray(X, dtype=np.float64)
        if X.shape[0] < self.k:
            raise ValueError("n_samples=%d should be >= k=%d" % (
                X.shape[0], self.k))
        X = as_float_array(X, copy=False)
        return X

    def _check_test_data(self, X):
        X = atleast2d_or_csr(X)
        n_samples, n_features = X.shape
        expected_n_features = self.cluster_centers_.shape[1]
        if not n_features == expected_n_features:
            raise ValueError("Incorrect number of features. "
                             "Got %d features, expected %d" % (
                                 n_features, expected_n_features))
        return X

    def _check_fitted(self):
        if not hasattr(self, "cluster_centers_"):
            raise AttributeError("Model has not been trained yet.")

    def fit(self, X, y=None):
        """Compute k-means"""
        self.random_state = check_random_state(self.random_state)
        X = self._check_fit_data(X)

        self.cluster_centers_, self.labels_, self.inertia_ = k_means(
            X, k=self.k, init=self.init, n_init=self.n_init,
            max_iter=self.max_iter, verbose=self.verbose,
            precompute_distances=self.precompute_distances,
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
        self._check_fitted()
        X = self._check_test_data(X)
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
        self._check_fitted()
        X = self._check_test_data(X)
        x_squared_norms = _squared_norms(X)
        return _labels_inertia(X, x_squared_norms, self.cluster_centers_)[0]

    def score(self, X):
        """Opposite of the value of X on the K-means objective.

        Parameters
        ----------
        X: {array-like, sparse matrix}, shape = [n_samples, n_features]
            New data.

        Returns
        -------
        score: float
            Opposite of the value of X on the K-means objective.
        """
        self._check_fitted()
        X = self._check_test_data(X)
        x_squared_norms = _squared_norms(X)
        return -_labels_inertia(X, x_squared_norms, self.cluster_centers_)[1]


def _mini_batch_step(X, x_squared_norms, centers, counts,
                     old_center_buffer, compute_squared_diff,
                     distances=None):
    """Incremental update of the centers for the Minibatch K-Means algorithm

    Parameters
    ----------

    X: array, shape (n_samples, n_features)
        The original data array.

    x_squared_norms: array, shape (n_samples,)
        Squared euclidean norm of each data point.

    centers: array, shape (k, n_features)
        The cluster centers. This array is MODIFIED IN PLACE

    counts: array, shape (k,)
         The vector in which we keep track of the numbers of elements in a
         cluster. This array is MODIFIED IN PLACE

    distances: array, dtype float64, shape (n_samples), optional
        If not None, should be a pre-allocated array that will be used to store
        the distances of each sample to it's closest center.
    """
    # Perform label assignement to nearest centers
    nearest_center, inertia = _labels_inertia(X, x_squared_norms, centers,
                                              distances=distances)

    # implementation for the sparse CSR reprensation completely written in
    # cython
    if sp.issparse(X):
        return inertia, _k_means._mini_batch_update_csr(
            X, x_squared_norms, centers, counts, nearest_center,
            old_center_buffer, compute_squared_diff)

    # dense variant in mostly numpy (not as memory efficient though)
    k = centers.shape[0]
    squared_diff = 0.0
    for center_idx in range(k):
        # find points from minibatch that are assigned to this center
        center_mask = nearest_center == center_idx
        count = center_mask.sum()

        if count > 0:
            if compute_squared_diff:
                old_center_buffer[:] = centers[center_idx]

            # inplace remove previous count scaling
            centers[center_idx] *= counts[center_idx]

            # inplace sum with new points members of this cluster
            centers[center_idx] += np.sum(X[center_mask], axis=0)

            # update the count statistics for this center
            counts[center_idx] += count

            # inplace rescale to compute mean of all points (old and new)
            centers[center_idx] /= counts[center_idx]

            # update the squared diff if necessary
            if compute_squared_diff:
                squared_diff += np.sum(
                    (centers[center_idx] - old_center_buffer) ** 2)

    return inertia, squared_diff


def _mini_batch_convergence(model, iteration_idx, n_iterations, tol,
                            n_samples, centers_squared_diff, batch_inertia,
                            context, verbose=0):
    """Helper function to encapsulte the early stopping logic"""
    # Normalize inertia to be able to compare values when
    # batch_size changes
    batch_inertia /= model.batch_size
    centers_squared_diff /= model.batch_size

    # Compute an Exponentially Weighted Average of the squared
    # diff to monitor the convergence while discarding
    # minibatch-local stochastic variability:
    # https://en.wikipedia.org/wiki/Moving_average
    ewa_diff = context.get('ewa_diff')
    ewa_inertia = context.get('ewa_inertia')
    if ewa_diff is None:
        ewa_diff = centers_squared_diff
        ewa_inertia = batch_inertia
    else:
        alpha = float(model.batch_size) * 2.0 / (n_samples + 1)
        alpha = 1.0 if alpha > 1.0 else alpha
        ewa_diff = ewa_diff * (1 - alpha) + centers_squared_diff * alpha
        ewa_inertia = ewa_inertia * (1 - alpha) + batch_inertia * alpha

    # Log progress to be able to monitor convergence
    if verbose:
        progress_msg = (
            'Minibatch iteration %d/%d:'
            'mean batch inertia: %f, ewa inertia: %f ' % (
                iteration_idx + 1, n_iterations, batch_inertia,
                ewa_inertia))
        print progress_msg

    # Early stopping based on absolute tolerance on squared change of
    # centers postion (using EWA smoothing)
    if tol > 0.0 and ewa_diff < tol:
        if verbose:
            print 'Converged (small centers change) at iteration %d/%d' % (
                iteration_idx + 1, n_iterations)
        return True

    # Early stopping heuristic due to lack of improvement on smoothed inertia
    ewa_inertia_min = context.get('ewa_inertia_min')
    no_improvement = context.get('no_improvement', 0)
    if (ewa_inertia_min is None or ewa_inertia < ewa_inertia_min):
        no_improvement = 0
        ewa_inertia_min = ewa_inertia
    else:
        no_improvement += 1

    if (model.max_no_improvement is not None
        and no_improvement >= model.max_no_improvement):
        if verbose:
            print ('Converged (lack of improvement in inertia)'
                   ' at iteration %d/%d' % (
                       iteration_idx + 1, n_iterations))
        return True

    # update the convergence context to maintain state across sucessive calls:
    context['ewa_diff'] = ewa_diff
    context['ewa_inertia'] = ewa_inertia
    context['ewa_inertia_min'] = ewa_inertia_min
    context['no_improvement'] = no_improvement
    return False


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

    init_size: int, optional, default: 3 * batch_size
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
        Compute a partial K-Means clustering for streaming large scale data
        into the estimator with incremental fitting.

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
                 init_size=None, n_init=3, chunk_size=None):

        super(MiniBatchKMeans, self).__init__(k=k, init=init,
              max_iter=max_iter, verbose=verbose, random_state=random_state,
              tol=tol, n_init=n_init)

        self.max_no_improvement = max_no_improvement
        if chunk_size is not None:
            warnings.warn(
                "chunk_size is deprecated in 0.10, use batch_size instead")
            batch_size = chunk_size
        self.batch_size = batch_size
        self.compute_labels = compute_labels
        self.init_size = batch_size if init_size is None else 3 * init_size

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
        n_samples, n_features = X.shape
        if n_samples < self.k:
            raise ValueError("Number of samples smaller than number "\
                             "of clusters.")

        if hasattr(self.init, '__array__'):
            self.init = np.ascontiguousarray(self.init, dtype=np.float64)

        x_squared_norms = _squared_norms(X)

        if self.tol > 0.0:
            if not sp.issparse(X):
                mean_variance = np.mean(np.var(X, 0))
            else:
                mean_variance = np.mean(mean_variance_axis0(X)[1])
            tol = self.tol * mean_variance

            # using tol-based early stopping needs the allocation of a
            # dedicated before which can be expensive for high dim data:
            # hence we allocate it outside of the main loop
            old_center_buffer = np.zeros(n_features, np.double)
        else:
            tol = 0.0
            # no need for the center buffer if tol-based early stopping is
            # disabled
            old_center_buffer = np.zeros(0, np.double)

        distances = np.zeros(self.batch_size, dtype=np.float64)
        n_batches = int(np.ceil(float(n_samples) / self.batch_size))
        n_iterations = int(self.max_iter * n_batches)

        init_size = self.init_size
        if init_size > n_samples:
            init_size = n_samples

        validation_indices = self.random_state.random_integers(
                0, n_samples - 1, init_size)
        X_valid = X[validation_indices]
        x_squared_norms_valid = x_squared_norms[validation_indices]

        # perform several inits with random sub-sets
        best_inertia = None
        for init_idx in range(self.n_init):
            if self.verbose:
                print "Init %d/%d with method: %s" % (
                    init_idx + 1, self.n_init, self.init)
            counts = np.zeros(self.k, dtype=np.int32)

            # TODO: once the `k_means` function works with sparse input we
            # should refactor the following init to use it instead.

            # Initialize the centers using only a fraction of the data as we
            # expect n_samples to be very large when using MiniBatchKMeans
            cluster_centers = _init_centroids(
                X, self.k, self.init,
                random_state=self.random_state,
                x_squared_norms=x_squared_norms,
                init_size=init_size)

            # Compute the label assignement on the init dataset
            batch_inertia, centers_squared_diff = _mini_batch_step(
                X_valid, x_squared_norms[validation_indices],
                cluster_centers, counts, old_center_buffer, False,
                distances=distances)

            # Keep only the best cluster centers across independant inits on
            # the common validation set
            _, inertia = _labels_inertia(X_valid, x_squared_norms_valid,
                                         cluster_centers)
            if self.verbose:
                print "Inertia for init %d/%d: %f" % (
                    init_idx + 1, self.n_init, inertia)
            if best_inertia is None or inertia < best_inertia:
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_inertia = inertia

        # Empty context to be used inplace by the convergence check routine
        convergence_context = {}

        # Perform the iterative optimization untill the final convergence
        # criterion
        for iteration_idx in xrange(n_iterations):

            # Sample the minibatch from the full dataset
            minibatch_indices = self.random_state.random_integers(
                0, n_samples - 1, self.batch_size)

            # Perform the actual update step on the minibatch data
            batch_inertia, centers_squared_diff = _mini_batch_step(
                X[minibatch_indices], x_squared_norms[minibatch_indices],
                self.cluster_centers_, self.counts_,
                old_center_buffer, tol > 0.0, distances=distances)

            # Monitor the convergence and do early stopping if necessary
            if _mini_batch_convergence(
                self, iteration_idx, n_iterations, tol, n_samples,
                centers_squared_diff, batch_inertia, convergence_context,
                verbose=self.verbose):
                break

        if self.compute_labels:
            if self.verbose:
                print 'Computing label assignements and total inertia'
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

        X = check_arrays(X, sparse_format="csr", copy=False)[0]
        n_samples, n_features = X.shape
        if hasattr(self.init, '__array__'):
            self.init = np.ascontiguousarray(self.init, dtype=np.float64)

        if n_samples == 0:
            return self

        x_squared_norms = _squared_norms(X)

        if (not hasattr(self, 'counts_')
            or not hasattr(self, 'cluster_centers_')):
            # this is the first call partial_fit on this object:
            # initialize the cluster centers
            self.cluster_centers_ = _init_centroids(
                X, self.k, self.init, random_state=self.random_state,
                x_squared_norms=x_squared_norms, init_size=self.init_size)

            self.counts_ = np.zeros(self.k, dtype=np.int32)

        _mini_batch_step(X, x_squared_norms, self.cluster_centers_,
                         self.counts_, np.zeros(0, np.double), 0)

        if self.compute_labels:
            self.labels_, self.inertia_ = _labels_inertia(
                X, x_squared_norms, self.cluster_centers_)

        return self
