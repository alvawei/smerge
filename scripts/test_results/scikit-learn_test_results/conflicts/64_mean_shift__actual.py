""" Algorithms for clustering : Meanshift,  Affinity propagation and spectral
clustering.

Authors: Conrad Lee conradlee@gmail.com
         Alexandre Gramfort alexandre.gramfort@inria.fr
         Gael Varoquaux gael.varoquaux@normalesup.org
"""

from math import floor
import numpy as np

from ..base import BaseEstimator
from ..metrics.pairwise import euclidean_distances


def estimate_bandwidth(X, quantile=0.3):
    """Estimate the bandwith ie the radius to use with an RBF kernel
    in the MeanShift algorithm

    X: array [n_samples, n_features]
        Input points

    quantile: float, default 0.3
        should be between [0, 1]
        0.5 means that the median is all pairwise distances is used
    """
    distances = euclidean_distances(X, X)
    distances = np.triu(distances, 1)
    distances_sorted = np.sort(distances[distances > 0])
    bandwidth = distances_sorted[floor(quantile * len(distances_sorted))]
    return bandwidth


def mean_shift(X, bandwidth=None):
    """Perform MeanShift Clustering of data using a flat kernel

    Parameters
    ----------

    X : array [n_samples, n_features]
        Input points

    bandwidth : float, optional
        kernel bandwidth
        If bandwidth is not defined, it is set using
        a heuristic given by the median of all pairwise distances

    Returns
    -------

    cluster_centers : array [n_clusters, n_features]
        Coordinates of cluster centers

    labels : array [n_samples]
        cluster labels for each point

    Notes
    -----
    See examples/plot_meanshift.py for an example.

    K. Funkunaga and L.D. Hosteler, "The Estimation of the Gradient of a
    Density Function, with Applications in Pattern Recognition"

    """
    if bandwidth is None:
        bandwidth = estimate_bandwidth(X)
    n_points, n_features = X.shape
    n_clusters = 0
    bandwidth_squared = bandwidth ** 2
    points_idx_init = np.arange(n_points)
    stop_thresh = 1e-3 * bandwidth  # when mean has converged
    cluster_centers = []  # center of clusters
    # track if a points been seen already
    been_visited_flag = np.zeros(n_points, dtype=np.bool)
    # number of points to possibly use as initilization points
    n_points_init = n_points
    # used to resolve conflicts on cluster membership
    cluster_votes = []
    random_state = np.random.RandomState(0)
    while n_points_init:
        # pick a random seed point
        tmp_index = random_state.randint(n_points_init)
        # use this point as start of mean
        start_idx = points_idx_init[tmp_index]
        my_mean = X[start_idx, :]  # intilize mean to this points location
        # points that will get added to this cluster
        my_members = np.zeros(n_points, dtype=np.bool)
        # used to resolve conflicts on cluster membership
        this_cluster_votes = np.zeros(n_points, dtype=np.uint16)
        while True:  # loop until convergence
            # dist squared from mean to all points still active
            sqrt_dist_to_all = np.sum((my_mean - X) ** 2, axis=1)
            # points within bandwidth
            in_idx = sqrt_dist_to_all < bandwidth_squared
            # add a vote for all the in points belonging to this cluster
            this_cluster_votes[in_idx] += 1
            my_old_mean = my_mean  # save the old mean
            my_mean = np.mean(X[in_idx, :], axis=0)  # compute the new mean
            # add any point within bandwidth to the cluster
            my_members = np.logical_or(my_members, in_idx)
            # mark that these points have been visited
            been_visited_flag[my_members] = True
            if np.linalg.norm(my_mean - my_old_mean) < stop_thresh:
                # check for merge possibilities
                merge_with = -1
                for c in range(n_clusters):
                    # distance from possible new clust max to old clust max
                    dist_to_other = np.linalg.norm(my_mean -
                                                        cluster_centers[c])
                    # if its within bandwidth/2 merge new and old
                    if dist_to_other < bandwidth / 2:
                        merge_with = c
                break
                if merge_with >= 0:  # something to merge
                    # record the max as the mean of the two merged
                    # (I know biased twoards new ones)
                    cluster_centers[merge_with] = 0.5 * (my_mean +
                                                cluster_centers[merge_with])
                    # add these votes to the merged cluster
                    cluster_votes[merge_with] += this_cluster_votes
                else:  # its a new cluster
                    n_clusters += 1  # increment clusters
                    cluster_centers.append(my_mean)  # record the mean
                    cluster_votes.append(this_cluster_votes)
                break
        # we can initialize with any of the points not yet visited
        points_idx_init = np.where(been_visited_flag == False)[0]
        n_points_init = points_idx_init.size  # number of active points in set
    # a point belongs to the cluster with the most votes
    labels = np.argmax(cluster_votes, axis=0)
    return cluster_centers, labels



















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
        the seeds are calculated by clustering.get_bin_seeds
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

    Because this implementation uses a flat kernel and
    a Ball Tree to look up members of each kernel, the complexity will is
    to O(T*n*log(n)) in lower dimensions, with n the number of samples
    and T the number of points. In higher dimensions the complexity will
    tend towards O(T*n^2).

    Scalability can be boosted by using fewer seeds, for examply by using
    a higher value of min_bin_freq in the get_bin_seeds function.

    Note that the estimate_bandwidth function is much less scalable than
    the mean shift algorithm and will be the bottleneck if it is used.

    """
    def __init__(self, bandwidth=None, seeds=None, bin_seeding=False,
                 cluster_all=True):
        self.bandwidth = bandwidth
        self.seeds = seeds
        self.bin_seeding = bin_seeding
        self.cluster_all = cluster_all
        self.cluster_centers_ = None
        self.labels_ = None
    def fit(self, X):
        """ Compute MeanShift

            Parameters
            -----------
            X : array [n_samples, n_features]
                Input points

        """
        self.cluster_centers_, self.labels_ = mean_shift(X, self.bandwidth)
        return self



