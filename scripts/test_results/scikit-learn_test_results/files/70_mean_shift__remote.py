""" Algorithms for clustering : Meanshift,  Affinity propagation and spectral
clustering.

Authors: Conrad Lee conradlee@gmail.com
         Alexandre Gramfort alexandre.gramfort@inria.fr
         Gael Varoquaux gael.varoquaux@normalesup.org
"""

from collections import defaultdict
import numpy as np

from ..utils import extmath, check_random_state
from ..base import BaseEstimator
from ..ball_tree import BallTree


def estimate_bandwidth(X, quantile=0.3, n_samples=None, random_state=0):
    """Estimate the bandwith to use with MeanShift algorithm

    Parameters
    ----------
    X: array [n_samples, n_features]
        Input points

    quantile: float, default 0.3
        should be between [0, 1]
        0.5 means that the median is all pairwise distances is used

    n_samples: int
        The number of samples to use. If None, all samples are used.

    random_state: int or RandomState
        Pseudo number generator state used for random sampling.

    Returns
    -------
    bandwidth: float
        The bandwidth parameter
    """
    random_state = check_random_state(random_state)
    if n_samples is not None:
        idx = random_state.permutation(X.shape[0])[:n_samples]
        X = X[idx]
    d, _ = BallTree(X).query(X, int(X.shape[0] * quantile),
                             return_distance=True)
    bandwidth = np.mean(np.max(d, axis=1))
    return bandwidth


def mean_shift(X, bandwidth=None, seeds=None, bucket_seeding=False,
               cluster_all=True, max_iterations=300):
    """Perform MeanShift Clustering of data using a flat kernel

    Seed using a bucketing/binning/discretizing technique for scalability.

    Parameters
    ----------

    X : array [n_samples, n_features]
        Input points

    bandwidth : float, optional
        kernel bandwidth
        If bandwidth is not defined, it is set using
        a heuristic given by the median of all pairwise distances

    seeds: array [n_seeds, n_features]
        point used as initial kernel locations

    bucket_seeding: boolean
        If true, initial kernel locations are not locations of all
        points, but rather the location of the discretized version of
        points, where points are discretized onto a grid whose coarseness
        corresponds to the bandwidth. Setting this option to True will speed
        up the algorithm because fewer seeds will be initialized.
        default value: False
        Ignored in seeds argument is not none

    min_bin_freq: int, optional
       To speed up the algorithm, accept only those bins with at least
       min_bin_freq points as seeds. If not defined, set to 1.

    Returns
    -------

    cluster_centers : array [n_clusters, n_features]
        Coordinates of cluster centers

    labels : array [n_samples]
        cluster labels for each point

    Notes
    -----
    See examples/plot_meanshift.py for an example.

    """

    if bandwidth is None:
        bandwidth = estimate_bandwidth(X)
    if seeds is None:
        if bucket_seeding:
            seeds = get_bucket_seeds(X, bandwidth)
        else:
            seeds = X
    n_points, n_features = X.shape
    stop_thresh = 0.1 * bandwidth  # when mean has converged
    center_intensity_dict = {}
    ball_tree = BallTree(X)  # to efficiently look up nearby points

    # For each seed, climb gradient until convergence or max_iterations
    for my_mean in seeds:
        completed_iterations = 0
        while True:
            # Find mean of points within bandwidth
            points_within = X[ball_tree.query_radius([my_mean], bandwidth)[0]]
            if len(points_within) == 0:
                break  # Depending on seeding strategy this condition may occur
            my_old_mean = my_mean  # save the old mean
            my_mean = np.mean(points_within, axis=0)
            # If converged or at max_iterations, add the cluster
            if extmath.norm(my_mean - my_old_mean) < stop_thresh or \
                   completed_iterations == max_iterations:
                center_intensity_dict[tuple(my_mean)] = len(points_within)
                break
            completed_iterations += 1

    # POST PROCESSING: remove near duplicate points
    # If the distance between two kernels is less than the bandwidth,
    # then we have to remove one because it is a duplicate. Remove the
    # one with fewer points.
    sorted_by_intensity = sorted(center_intensity_dict.items(),
                                 key=lambda tup: tup[1], reverse=True)
    sorted_centers = np.array([tup[0] for tup in sorted_by_intensity])
    unique = np.ones(len(sorted_centers), dtype=np.bool)
    cc_tree = BallTree(sorted_centers)
    for i, center in enumerate(sorted_centers):
        if unique[i]:
            neighbor_idxs = cc_tree.query_radius([center], bandwidth)[0]
            unique[neighbor_idxs] = 0
            unique[i] = 1  # leave the current point as uniuqe
    cluster_centers = sorted_centers[unique]

    # ASSIGN LABELS: a point belongs to the cluster that it is closest to
    centers_tree = BallTree(cluster_centers)
    if len(cluster_centers) < 65535:
        labels = np.zeros(n_points, dtype=np.uint16)
    else:
        labels = np.zeros(n_points, dtype=np.uint32)
    distances, idxs = centers_tree.query(X, 1)
    if cluster_all:
        labels = idxs.flatten()
    else:
        labels[:] = -1
        ind = np.where(distances.flatten() < bandwidth)[0]
        labels[ind] = idxs.flatten()[ind]
    return cluster_centers, labels


def get_bucket_seeds(X, bin_size, min_bin_freq=1):
    """
    Finds seeds for clustering.mean_shift by first bucketing/discretizing
    data onto a grid whose lines are spaced bin_size apart, and then
    choosing those buckets with at least min_bin_freq points.
    Parameters
    ----------

    X : array [n_samples, n_features]
        Input points, the same points that will be used in mean_shift

    bin_size: float
        Controls the coarseness of the discretization. Smaller values lead
        to more seeding (which is computationally more expensive). If you're
        not sure how to set this, set it to the value of the bandwidth used
        in clustering.mean_shift

    min_bin_freq: integer, default 1
        Only bins with at least min_bin_freq will be selected as seeds.
        Raising this value decreases the number of seeds found, which
        makes mean_shift computationally cheaper.
    Returns
    -------

    bin_seeds : array [n_samples, n_features]
        points used as initial kernel posistions in clustering.mean_shift
    """

    # Discretize (i.e., quantize, bin) points to bins
    bin_sizes = defaultdict(int)
    discretized_points = X.copy() / bin_size
    discretized_points = np.cast[np.int32](discretized_points)
    for discretized_point in discretized_points:
        bin_sizes[tuple(discretized_point)] += 1

    # Select only those bins as seeds which have enough members
    bin_seeds = np.array([point for point, freq in bin_sizes.iteritems() if \
                          freq >= min_bin_freq], dtype=np.float32)
    bin_seeds = bin_seeds * bin_size
    return bin_seeds

##############################################################################


class MeanShift(BaseEstimator):
    """MeanShift clustering


    Parameters
    ----------

    bandwidth: float, optional
        Bandwith used in the RBF kernel
        If not set, the bandwidth is estimated.
        See clustering.estimate_bandwidth

    seeds: array [n_samples, n_features], optional
        Seeds used to initialize kernels. If not set,
        the seeds are calculated by clustering.get_bucket_seeds
        with bandwidth as the grid size and default values for
        other parameters.

    cluster_all: boolean, default True
        If true, then all points are clustered, even those orphans that are
        not within any kernel. Orphans are assigned to the nearest kernel.
        If false, then orphans are given cluster label -1.
    Methods
    -------

    fit(X):
        Compute MeanShift clustering

    Attributes
    ----------

    cluster_centers_: array, [n_clusters, n_features]
        Coordinates of cluster centers

    labels_:
        Labels of each point

    Notes
    -----

    Reference:

    Dorin Comaniciu and Peter Meer, "Mean Shift: A robust approach toward
    feature space analysis". IEEE Transactions on Pattern Analysis and
    Machine Intelligence. 2002. pp. 603-619.

    Scalability:

    In general, the algorithmic complexity of the mean shift algorithm
    is O(T n^2) with n the number of samples and T the number of
    points.

    Because this implementation uses a flat kernel and
    a KD-Tree to look up members of each kernel, the complexity will tend
    to O(T n*log(n)). In higher dimensions,  finding nearest neighbors
    using the KD-Tree may become more expensive.

    Scalability can be boosted by using fewer seeds, for examply by using
    a higher value of min_bin_freq in the get_bucket_seeds function.

    Note that the estimate_bandwidth function is much less scalable than
    the mean shift algorithm and will be the bottleneck if it is used.

    """

    def __init__(self, bandwidth=None, seeds=None, bucket_seeding=False,
                 cluster_all=True):
        self.bandwidth = bandwidth
        self.seeds = seeds
        self.bucket_seeding = bucket_seeding
        self.cluster_all = cluster_all
        self.cluster_centers_ = None
        self.labels_ = None

    def fit(self, X, **params):
        """ Compute MeanShift

            Parameters
            -----------
            X : array [n_samples, n_features]
                Input points

        """
        self._set_params(**params)
        self.cluster_centers_, self.labels_ = \
                               mean_shift(X,
                                          bandwidth=self.bandwidth,
                                          seeds=self.seeds,
                                          bucket_seeding=self.bucket_seeding,
                                          cluster_all=self.cluster_all)
        return self
