# Hidden Markov Models
#
# Author: Ron Weiss <ronweiss@gmail.com>

"""
The :mod:`sklearn.hmm` module implements hidden Markov models.

**Warning:** :mod:`sklearn.hmm` is orphaned, undocumented and has known
numerical stability issues. If nobody volunteers to write documentation and
make it more stable, this module will be removed in version 0.11.
"""

import string

import numpy as np

from .utils import check_random_state
from .utils.extmath import logsumexp
from .base import BaseEstimator
from .mixture import (
    GMM, log_multivariate_normal_density, sample_gaussian,
    distribute_covar_matrix_to_match_covariance_type, _validate_covars)
from . import cluster
import warnings
warnings.warn('sklearn.hmm is orphaned, undocumented and has known numerical'
              ' stability issues. If nobody volunteers to write documentation'
              ' and make it more stable, this module will be removed in'
              ' version 0.11.')

ZEROLOGPROB = -1e200
EPS = np.finfo(float).eps
NEGINF = - np.inf


def normalize(A, axis=None):
    """ Normalize the input array so that it sums to 1.

    Parameters
    ----------
    A: array, shape (n_samples, n_features)
       Non-normalized input data
    axis: int
          dimension along which normalization is performed

    Returns
    -------
    normalized_A: array, shape (n_samples, n_features)
        A with values normalized (summing to 1) along the prescribed axis

    WARNING: Modifies inplace the array
    """
    A += EPS
    Asum = A.sum(axis)
    if axis and A.ndim > 1:
        # Make sure we don't divide by zero.
        Asum[Asum == 0] = 1
        shape = list(A.shape)
        shape[axis] = 1
        Asum.shape = shape
    return A / Asum


class _BaseHMM(BaseEstimator):
    """Hidden Markov Model base class.

    Representation of a hidden Markov model probability distribution.
    This class allows for easy evaluation of, sampling from, and
    maximum-likelihood estimation of the parameters of a HMM.

    See the instance documentation for details specific to a
    particular object.

    Attributes
    ----------
    n_components : int (read-only)
        Number of states in the model.

    See Also
    --------
    GMM : Gaussian mixture model
    """

    # This class implements the public interface to all HMMs that
    # derive from it, including all of the machinery for the
    # forward-backward and Viterbi algorithms.  Subclasses need only
    # implement _generate_sample_from_state(), _compute_log_likelihood(),
    # _init(), _initialize_sufficient_statistics(),
    # _accumulate_sufficient_statistics(), and _do_mstep(), all of
    # which depend on the specific emission distribution.
    #
    # Subclasses will probably also want to implement properties for
    # the emission distribution parameters to expose them publically.

    def __init__(self, n_components=1, startprob=None, transmat=None,
                 startprob_prior=None, transmat_prior=None):
        self.n_components = n_components

        if startprob is None:
            startprob = np.tile(1.0 / n_components, n_components)
        self._set_startprob(startprob)

        if startprob_prior is None:
            startprob_prior = 1.0
        self.startprob_prior = startprob_prior

        if transmat is None:
            transmat = np.tile(1.0 / n_components,
                    (n_components, n_components))
        self._set_transmat(transmat)

        if transmat_prior is None:
            transmat_prior = 1.0
        self.transmat_prior = transmat_prior

    def eval(self, obs, maxrank=None, beamlogprob=NEGINF):
        """Compute the log probability under the model and compute posteriors

        Implements rank and beam pruning in the forward-backward
        algorithm to speed up inference in large models.

        Parameters
        ----------
        obs : array_like, shape (n, n_features)
            Sequence of n_features-dimensional data points.  Each row
            corresponds to a single point in the sequence.
        maxrank : int
            Maximum rank to evaluate for rank pruning.  If not None,
            only consider the top `maxrank` states in the inner
            sum of the forward algorithm recursion.  Defaults to None
            (no rank pruning).  See The HTK Book for more details.
        beamlogprob : float
            Width of the beam-pruning beam in log-probability units.
            Defaults to -numpy.Inf (no beam pruning).  See The HTK
            Book for more details.

        Returns
        -------
        logprob : array_like, shape (n,)
            Log probabilities of the sequence `obs`
        posteriors: array_like, shape (n, n_components)
            Posterior probabilities of each state for each
            observation

        See Also
        --------
        score : Compute the log probability under the model
        decode : Find most likely state sequence corresponding to a `obs`
        """
        obs = np.asarray(obs)
        framelogprob = self._compute_log_likelihood(obs)
        logprob, fwdlattice = self._do_forward_pass(framelogprob, maxrank,
                                                    beamlogprob)
        bwdlattice = self._do_backward_pass(framelogprob, fwdlattice, maxrank,
                                            beamlogprob)
        gamma = fwdlattice + bwdlattice
        # gamma is guaranteed to be correctly normalized by logprob at
        # all frames, unless we do approximate inference using pruning.
        # So, we will normalize each frame explicitly in case we
        # pruned too aggressively.
        posteriors = np.exp(gamma.T - logsumexp(gamma, axis=1)).T
        posteriors += np.finfo(np.float32).eps
        posteriors /= np.sum(posteriors, axis=1).reshape((-1, 1))
        return logprob, posteriors

    def score(self, obs, maxrank=None, beamlogprob=NEGINF):
        """Compute the log probability under the model.

        Parameters
        ----------
        obs : array_like, shape (n, n_features)
            Sequence of n_features-dimensional data points.  Each row
            corresponds to a single data point.
        maxrank : int
            Maximum rank to evaluate for rank pruning.  If not None,
            only consider the top `maxrank` states in the inner
            sum of the forward algorithm recursion.  Defaults to None
            (no rank pruning).  See The HTK Book for more details.
        beamlogprob : float
            Width of the beam-pruning beam in log-probability units.
            Defaults to -numpy.Inf (no beam pruning).  See The HTK
            Book for more details.

        Returns
        -------
        logprob : array_like, shape (n,)
            Log probabilities of each data point in `obs`

        See Also
        --------
        eval : Compute the log probability under the model and posteriors
        decode : Find most likely state sequence corresponding to a `obs`
        """
        obs = np.asarray(obs)
        framelogprob = self._compute_log_likelihood(obs)
        logprob, fwdlattice = self._do_forward_pass(framelogprob, maxrank,
                                                    beamlogprob)
        return logprob

    def decode(self, obs, maxrank=None, beamlogprob=NEGINF):
        """Find most likely state sequence corresponding to `obs`.

        Uses the Viterbi algorithm.

        Parameters
        ----------
        obs : array_like, shape (n, n_features)
            List of n_features-dimensional data points.  Each row
            corresponds to a single data point.
        maxrank : int
            Maximum rank to evaluate for rank pruning.  If not None,
            only consider the top `maxrank` states in the inner
            sum of the forward algorithm recursion.  Defaults to None
            (no rank pruning).  See The HTK Book for more details.
        beamlogprob : float
            Width of the beam-pruning beam in log-probability units.
            Defaults to -numpy.Inf (no beam pruning).  See The HTK
            Book for more details.

        Returns
        -------
        viterbi_logprob : float
            Log probability of the maximum likelihood path through the HMM
        states : array_like, shape (n,)
            Index of the most likely states for each observation

        See Also
        --------
        eval : Compute the log probability under the model and posteriors
        score : Compute the log probability under the model
        """
        obs = np.asarray(obs)
        framelogprob = self._compute_log_likelihood(obs)
        logprob, state_sequence = self._do_viterbi_pass(framelogprob, maxrank,
                                                        beamlogprob)
        return logprob, state_sequence

    def predict(self, obs, **kwargs):
        """Find most likely state sequence corresponding to `obs`.

        Parameters
        ----------
        obs : array_like, shape (n, n_features)
            List of n_features-dimensional data points.  Each row
            corresponds to a single data point.
        maxrank : int
            Maximum rank to evaluate for rank pruning.  If not None,
            only consider the top `maxrank` states in the inner
            sum of the forward algorithm recursion.  Defaults to None
            (no rank pruning).  See The HTK Book for more details.
        beamlogprob : float
            Width of the beam-pruning beam in log-probability units.
            Defaults to -numpy.Inf (no beam pruning).  See The HTK
            Book for more details.

        Returns
        -------
        states : array_like, shape (n,)
            Index of the most likely states for each observation
        """
        logprob, state_sequence = self.decode(obs, **kwargs)
        return state_sequence

    def predict_proba(self, obs, **kwargs):
        """Compute the posterior probability for each state in the model

        Parameters
        ----------
        obs : array_like, shape (n, n_features)
            List of n_features-dimensional data points.  Each row
            corresponds to a single data point.

        See eval() for a list of accepted keyword arguments.

        Returns
        -------
        T : array-like, shape (n, n_components)
            Returns the probability of the sample for each state in the model.
        """
        logprob, posteriors = self.eval(obs, **kwargs)
        return posteriors

    def rvs(self, n=1, random_state=None):
        """Generate random samples from the model.

        Parameters
        ----------
        n : int
            Number of samples to generate.

        Returns
        -------
        (obs, hidden_states) 
        obs : array_like, length `n` List of samples
        hidden_states : array_like, length `n` List of hidden states
        """
        random_state = check_random_state(random_state)

        startprob_pdf = self._get_startprob()
        startprob_cdf = np.cumsum(startprob_pdf)
        transmat_pdf = self._get_transmat()
        transmat_cdf = np.cumsum(transmat_pdf, 1)

        # Initial state.
        rand = random_state.rand()
        currstate = (startprob_cdf > rand).argmax()
        hidden_states = [currstate]
        obs = [self._generate_sample_from_state(
            currstate, random_state=random_state)]

        for x in xrange(n - 1):
            rand = random_state.rand()
            currstate = (transmat_cdf[currstate] > rand).argmax()
            hidden_states.append(currstate)
            obs.append(self._generate_sample_from_state(
                currstate, random_state=random_state))

        return np.array(obs), np.array(hidden_states, dtype=int)

    def fit(self, obs, n_iter=10, thresh=1e-2, params=string.ascii_letters,
            init_params=string.ascii_letters, maxrank=None,
            beamlogprob=NEGINF, **kwargs):
        """Estimate model parameters.

        An initialization step is performed before entering the EM
        algorithm. If you want to avoid this step, set the keyword
        argument init_params to the empty string ''. Likewise, if you
        would like just to do an initialization, call this method with
        n_iter=0.

        Parameters
        ----------
        obs : list
            List of array-like observation sequences (shape (n_i, n_features)).

        n_iter : int, optional
            Number of iterations to perform.

        thresh : float, optional
            Convergence threshold.

        params : string, optional
            Controls which parameters are updated in the training
            process.  Can contain any combination of 's' for startprob,
            't' for transmat, 'm' for means, and 'c' for covars, etc.
            Defaults to all parameters.

        init_params : string, optional
            Controls which parameters are initialized prior to
            training.  Can contain any combination of 's' for
            startprob, 't' for transmat, 'm' for means, and 'c' for
            covars, etc.  Defaults to all parameters.

        maxrank : int, optional
            Maximum rank to evaluate for rank pruning.  If not None,
            only consider the top `maxrank` states in the inner
            sum of the forward algorithm recursion.  Defaults to None
            (no rank pruning).  See "The HTK Book" for more details.

        beamlogprob : float, optional
            Width of the beam-pruning beam in log-probability units.
            Defaults to -numpy.Inf (no beam pruning).  See "The HTK
            Book" for more details.

        Notes
        -----
        In general, `logprob` should be non-decreasing unless
        aggressive pruning is used.  Decreasing `logprob` is generally
        a sign of overfitting (e.g. a covariance parameter getting too
        small).  You can fix this by getting more training data, or
        decreasing `covars_prior`.
        """
        self._init(obs, init_params)

        logprob = []
        for i in xrange(n_iter):
            # Expectation step
            stats = self._initialize_sufficient_statistics()
            curr_logprob = 0
            for seq in obs:
                framelogprob = self._compute_log_likelihood(seq)
                lpr, fwdlattice = self._do_forward_pass(framelogprob, maxrank,
                                                       beamlogprob)
                bwdlattice = self._do_backward_pass(framelogprob, fwdlattice,
                                                   maxrank, beamlogprob)
                gamma = fwdlattice + bwdlattice
                posteriors = np.exp(gamma.T - logsumexp(gamma, axis=1)).T
                curr_logprob += lpr
                self._accumulate_sufficient_statistics(
                    stats, seq, framelogprob, posteriors, fwdlattice,
                    bwdlattice, params)
            logprob.append(curr_logprob)

            # Check for convergence.
            if i > 0 and abs(logprob[-1] - logprob[-2]) < thresh:
                break

            # Maximization step
            self._do_mstep(stats, params, **kwargs)

        return self

    def _get_startprob(self):
        """Mixing startprob for each state."""
        return np.exp(self._log_startprob)

    def _set_startprob(self, startprob):
        if len(startprob) != self.n_components:
            raise ValueError('startprob must have length n_components')
        if not np.allclose(np.sum(startprob), 1.0):
            raise ValueError('startprob must sum to 1.0')

        self._log_startprob = np.log(np.asarray(startprob).copy())

    def _get_transmat(self):
        """Matrix of transition probabilities."""
        return np.exp(self._log_transmat)

    def _set_transmat(self, transmat):
        if (np.asarray(transmat).shape
                != (self.n_components, self.n_components)):
            raise ValueError('transmat must have shape ' +
                    '(n_components, n_components)')
        if not np.all(np.allclose(np.sum(transmat, axis=1), 1.0)):
            raise ValueError('Rows of transmat must sum to 1.0')

        self._log_transmat = np.log(np.asarray(transmat).copy())
        underflow_idx = np.isnan(self._log_transmat)
        self._log_transmat[underflow_idx] = NEGINF

    def _do_viterbi_pass(self, framelogprob, maxrank=None,
                         beamlogprob=NEGINF):
        nobs = len(framelogprob)
        lattice = np.zeros((nobs, self.n_components))
        traceback = np.zeros((nobs, self.n_components), dtype=np.int)

        lattice[0] = self._log_startprob + framelogprob[0]
        for n in xrange(1, nobs):
            idx = self._prune_states(lattice[n - 1], maxrank, beamlogprob)
            pr = self._log_transmat[idx].T + lattice[n - 1, idx]
            lattice[n] = np.max(pr, axis=1) + framelogprob[n]
            traceback[n] = np.argmax(pr, axis=1)
        lattice[lattice <= ZEROLOGPROB] = NEGINF

        # Do traceback.
        reverse_state_sequence = []
        s = lattice[-1].argmax()
        logprob = lattice[-1, s]
        for frame in reversed(traceback):
            reverse_state_sequence.append(s)
            s = frame[s]

        reverse_state_sequence.reverse()
        return logprob, np.array(reverse_state_sequence)

    def _do_forward_pass(self, framelogprob, maxrank=None,
                         beamlogprob=NEGINF):
        nobs = len(framelogprob)
        fwdlattice = np.zeros((nobs, self.n_components))

        fwdlattice[0] = self._log_startprob + framelogprob[0]
        for n in xrange(1, nobs):
            idx = self._prune_states(fwdlattice[n - 1], maxrank, beamlogprob)
            fwdlattice[n] = (logsumexp(self._log_transmat[idx].T
                                    + fwdlattice[n - 1, idx], axis=1)
                             + framelogprob[n])
        fwdlattice[fwdlattice <= ZEROLOGPROB] = NEGINF

        return logsumexp(fwdlattice[-1]), fwdlattice

    def _do_backward_pass(self, framelogprob, fwdlattice, maxrank=None,
                          beamlogprob=NEGINF):
        nobs = len(framelogprob)
        bwdlattice = np.zeros((nobs, self.n_components))

        for n in xrange(nobs - 1, 0, -1):
            # Do HTK style pruning (p. 137 of HTK Book version 3.4).
            # Don't bother computing backward probability if
            # fwdlattice * bwdlattice is more than a certain distance
            # from the total log likelihood.
            idx = self._prune_states(bwdlattice[n] + fwdlattice[n], None,
                                     -50)
            bwdlattice[n - 1] = logsumexp(self._log_transmat[:, idx] +
                                       bwdlattice[n, idx] +
                                       framelogprob[n, idx],
                                       axis=1)
        bwdlattice[bwdlattice <= ZEROLOGPROB] = NEGINF

        return bwdlattice

    def _prune_states(self, lattice_frame, maxrank, beamlogprob):
        """ Returns indices of the active states in `lattice_frame`
        after rank and beam pruning.
        """
        # Beam pruning
        threshlogprob = logsumexp(lattice_frame) + beamlogprob
        # Rank pruning
        if maxrank:
            # How big should our rank pruning histogram be?
            nbins = 3 * len(lattice_frame)

            lattice_min = lattice_frame[lattice_frame > ZEROLOGPROB].min() - 1
            hst, bin_edges = np.histogram(lattice_frame, bins=nbins,
                                    range=(lattice_min, lattice_frame.max()))

            # Want to look at the high ranks.
            hst = hst[::-1].cumsum()
            bin_edges = .5 * (bin_edges[:-1] + bin_edges[1:])
            bin_edges = bin_edges[::-1]

            rankthresh = bin_edges[hst >= min(maxrank,
                                              self.n_components)].max()

            # Only change the threshold if it is stricter than the beam
            # threshold.
            threshlogprob = max(threshlogprob, rankthresh)

        # Which states are active?
        state_idx, = np.nonzero(lattice_frame >= threshlogprob)
        return state_idx

    def _compute_log_likelihood(self, obs):
        pass

    def _generate_sample_from_state(self, state, random_state=None):
        pass

    def _init(self, obs, params):
        if 's' in params:
            self._set_startprob((1.0 / self.n_components) *
                                np.ones(self.n_components))
        if 't' in params:
            self._set_transmat(1.0 / self.n_components *
                               np.ones((self.n_components, self.n_components)))

    # Methods used by self.fit()

    def _initialize_sufficient_statistics(self):
        stats = {'nobs': 0,
                 'start': np.zeros(self.n_components),
                 'trans': np.zeros((self.n_components, self.n_components))}
        return stats

    def _accumulate_sufficient_statistics(self, stats, seq, framelogprob,
                                          posteriors, fwdlattice, bwdlattice,
                                          params):
        stats['nobs'] += 1
        if 's' in params:
            stats['start'] += posteriors[0]
        if 't' in params:
            for t in xrange(len(framelogprob)):
                zeta = (fwdlattice[t - 1][:, np.newaxis] + self._log_transmat
                        + framelogprob[t] + bwdlattice[t])
                stats['trans'] += np.exp(zeta - logsumexp(zeta))

    def _do_mstep(self, stats, params, **kwargs):
        # Based on Huang, Acero, Hon, "Spoken Language Processing",
        # p. 443 - 445
        if 's' in params:
            self._set_startprob(normalize(
                np.maximum(self.startprob_prior - 1.0 + stats['start'],
                           EPS)))
        if 't' in params:
            self._set_transmat(normalize(
                np.maximum(self.transmat_prior - 1.0 + stats['trans'],
                           EPS), axis=1))


class GaussianHMM(_BaseHMM):
    """Hidden Markov Model with Gaussian emissions

    Representation of a hidden Markov model probability distribution.
    This class allows for easy evaluation of, sampling from, and
    maximum-likelihood estimation of the parameters of a HMM.

    Parameters
    ----------
    n_components : int
        Number of states.

    _covariance_type : string
        String describing the type of covariance parameters to
        use.  Must be one of 'spherical', 'tied', 'diag', 'full'.
        Defaults to 'diag'.

    Attributes
    ----------
    covariance_type : string
        String describing the type of covariance parameters used by
        the model.  Must be one of 'spherical', 'tied', 'diag', 'full'.

    n_features : int
        Dimensionality of the Gaussian emissions.

    n_components : int
        Number of states in the model.

    transmat : array, shape (`n_components`, `n_components`)
        Matrix of transition probabilities between states.

    startprob : array, shape ('n_components`,)
        Initial state occupation distribution.

    means : array, shape (`n_components`, `n_features`)
        Mean parameters for each state.

    covars : array
        Covariance parameters for each state.  The shape depends on
        `_covariance_type`::
            (`n_components`,)                   if 'spherical',
            (`n_features`, `n_features`)              if 'tied',
            (`n_components`, `n_features`)           if 'diag',
            (`n_components`, `n_features`, `n_features`)  if 'full'

    Examples
    --------
    >>> from sklearn.hmm import GaussianHMM
    >>> GaussianHMM(n_components=2)
    ...                             #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    GaussianHMM(covariance_type=None, covars_prior=0.01, covars_weight=1,
    means_prior=None, means_weight=0, n_components=2, startprob=None,
    startprob_prior=1.0, transmat=None, transmat_prior=1.0)

    See Also
    --------
    GMM : Gaussian mixture model
    """

    def __init__(self, n_components=1, covariance_type='diag', startprob=None,
                 transmat=None, startprob_prior=None, transmat_prior=None,
                 means_prior=None, means_weight=0,
                 covars_prior=1e-2, covars_weight=1):
        super(GaussianHMM, self).__init__(n_components, startprob, transmat,
                                          startprob_prior=startprob_prior,
                                          transmat_prior=transmat_prior)

        self._covariance_type = covariance_type
        if not covariance_type in ['spherical', 'tied', 'diag', 'full']:
            raise ValueError('bad covariance_type')

        self.means_prior = means_prior
        self.means_weight = means_weight

        self.covars_prior = covars_prior
        self.covars_weight = covars_weight

    def _get_covars(self):
        """Return covars as a full matrix."""
        if self._covariance_type == 'full':
            return self._covars
        elif self._covariance_type == 'diag':
            return [np.diag(cov) for cov in self._covars]
        elif self._covariance_type == 'tied':
            return [self._covars] * self.n_components
        elif self._covariance_type == 'spherical':
            return [np.eye(self.n_features) * f for f in self._covars]

    def _set_covars(self, covars):
        covars = np.asarray(covars)
        _validate_covars(covars, self._covariance_type, self.n_components)
        self._covars = covars.copy()

    def _compute_log_likelihood(self, obs):
        return log_multivariate_normal_density(
            obs, self._means, self._covars, self._covariance_type)

    def _generate_sample_from_state(self, state, random_state=None):
        if self._covariance_type == 'tied':
            cv = self._covars
        else:
            cv = self._covars[state]
        return sample_gaussian(self._means[state], cv, self._covariance_type,
                               random_state=random_state)

    def _init(self, obs, params='stmc'):
        super(GaussianHMM, self)._init(obs, params=params)

        if (hasattr(self, 'n_features')
            and self.n_features != obs[0].shape[1]):
            raise ValueError('Unexpected number of dimensions, got %s but '
                             'expected %s' % (obs[0].shape[1],
                                              self.n_features))

        self.n_features = obs[0].shape[1]

        if 'm' in params:
            self._means = cluster.KMeans(
                k=self.n_components).fit(obs[0]).cluster_centers_
        if 'c' in params:
            cv = np.cov(obs[0].T)
            if not cv.shape:
                cv.shape = (1, 1)
            self._covars = distribute_covar_matrix_to_match_covariance_type(
                cv, self._covariance_type, self.n_components)

    def _initialize_sufficient_statistics(self):
        stats = super(GaussianHMM, self)._initialize_sufficient_statistics()
        stats['post'] = np.zeros(self.n_components)
        stats['obs'] = np.zeros((self.n_components, self.n_features))
        stats['obs**2'] = np.zeros((self.n_components, self.n_features))
        stats['obs*obs.T'] = np.zeros((self.n_components, self.n_features,
                                       self.n_features))
        return stats

    def _accumulate_sufficient_statistics(self, stats, obs, framelogprob,
                                          posteriors, fwdlattice, bwdlattice,
                                          params):
        super(GaussianHMM, self)._accumulate_sufficient_statistics(
            stats, obs, framelogprob, posteriors, fwdlattice, bwdlattice,
            params)

        if 'm' in params or 'c' in params:
            stats['post'] += posteriors.sum(axis=0)
            stats['obs'] += np.dot(posteriors.T, obs)

        if 'c' in params:
            if self._covariance_type in ('spherical', 'diag'):
                stats['obs**2'] += np.dot(posteriors.T, obs ** 2)
            elif self._covariance_type in ('tied', 'full'):
                for t, o in enumerate(obs):
                    obsobsT = np.outer(o, o)
                    for c in xrange(self.n_components):
                        stats['obs*obs.T'][c] += posteriors[t, c] * obsobsT

    def _do_mstep(self, stats, params, **kwargs):
        super(GaussianHMM, self)._do_mstep(stats, params)

        # Based on Huang, Acero, Hon, "Spoken Language Processing",
        # p. 443 - 445
        denom = stats['post'][:, np.newaxis]
        if 'm' in params:
            prior = self.means_prior
            weight = self.means_weight
            if prior is None:
                weight = 0
                prior = 0
            self._means = (weight * prior + stats['obs']) / (weight + denom)

        if 'c' in params:
            covars_prior = self.covars_prior
            covars_weight = self.covars_weight
            if covars_prior is None:
                covars_weight = 0
                covars_prior = 0

            means_prior = self.means_prior
            means_weight = self.means_weight
            if means_prior is None:
                means_weight = 0
                means_prior = 0
            meandiff = self._means - means_prior

            if self._covariance_type in ('spherical', 'diag'):
                cv_num = (means_weight * (meandiff) ** 2
                          + stats['obs**2']
                          - 2 * self._means * stats['obs']
                          + self._means ** 2 * denom)
                cv_den = max(covars_weight - 1, 0) + denom
                self._covars = (covars_prior + cv_num) / cv_den
                if self._covariance_type == 'spherical':
                    self._covars = np.tile(self._covars.mean(1)[:, np.newaxis],
                                           (1, self._covars.shape[1]))
            elif self._covariance_type in ('tied', 'full'):
                cvnum = np.empty((self.n_components, self.n_features,
                                  self.n_features))
                for c in xrange(self.n_components):
                    obsmean = np.outer(stats['obs'][c], self._means[c])

                    cvnum[c] = (means_weight * np.outer(meandiff[c],
                                                        meandiff[c])
                                + stats['obs*obs.T'][c]
                                - obsmean - obsmean.T
                                + np.outer(self._means[c], self._means[c])
                                * stats['post'][c])
                cvweight = max(covars_weight - self.n_features, 0)
                if self._covariance_type == 'tied':
                    self._covars = ((covars_prior + cvnum.sum(axis=0))
                                    / (cvweight + stats['post'].sum()))
                elif self._covariance_type == 'full':
                    self._covars = ((covars_prior + cvnum)
                                   / (cvweight + stats['post'][:, None, None]))


class MultinomialHMM(_BaseHMM):
    """Hidden Markov Model with multinomial (discrete) emissions

    Attributes
    ----------
    n_components : int
        Number of states in the model.

    n_symbols : int
        Number of possible symbols emitted by the model (in the observations).

    transmat : array, shape (`n_components`, `n_components`)
        Matrix of transition probabilities between states.

    startprob : array, shape ('n_components`,)
        Initial state occupation distribution.

    emissionprob : array, shape ('n_components`, 'n_symbols`)
        Probability of emitting a given symbol when in each state.

    Examples
    --------
    >>> from sklearn.hmm import MultinomialHMM
    >>> MultinomialHMM(n_components=2)
    ...                             #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    MultinomialHMM(n_components=2, startprob=None, startprob_prior=1.0,
             transmat=None, transmat_prior=1.0)

    See Also
    --------
    GaussianHMM : HMM with Gaussian emissions
    """

    def __init__(self, n_components=1, startprob=None, transmat=None,
                 startprob_prior=None, transmat_prior=None):
        """Create a hidden Markov model with multinomial emissions.

        Parameters
        ----------
        n_components : int
            Number of states.
        """
        super(MultinomialHMM, self).__init__(n_components, startprob, transmat,
                                             startprob_prior=startprob_prior,
                                             transmat_prior=transmat_prior)

    def _get_emissionprob(self):
        """Emission probability distribution for each state."""
        return np.exp(self._log_emissionprob)

    def _set_emissionprob(self, emissionprob):
        emissionprob = np.asarray(emissionprob)
        if hasattr(self, 'n_symbols') and \
               emissionprob.shape != (self.n_components, self.n_symbols):
            raise ValueError('emissionprob must have shape '
                             '(n_components, n_symbols)')

        self._log_emissionprob = np.log(emissionprob)
        underflow_idx = np.isnan(self._log_emissionprob)
        self._log_emissionprob[underflow_idx] = NEGINF
        self.n_symbols = self._log_emissionprob.shape[1]

    def _compute_log_likelihood(self, obs):
        return self._log_emissionprob[:, obs].T

    def _generate_sample_from_state(self, state, random_state=None):
        cdf = np.cumsum(self._get_emissionprob()[state])
        random_state = check_random_state(random_state)
        rand = random_state.rand()
        symbol = (cdf > rand).argmax()
        return symbol

    def _init(self, obs, params='ste'):
        super(MultinomialHMM, self)._init(obs, params=params)

        if 'e' in params:
            emissionprob = normalize(np.random.rand(self.n_components,
                                                    self.n_symbols), 1)
            self._set_emissionprob(emissionprob)

    def _initialize_sufficient_statistics(self):
        stats = super(MultinomialHMM, self)._initialize_sufficient_statistics()
        stats['obs'] = np.zeros((self.n_components, self.n_symbols))
        return stats

    def _accumulate_sufficient_statistics(self, stats, obs, framelogprob,
                                          posteriors, fwdlattice, bwdlattice,
                                          params):
        super(MultinomialHMM, self)._accumulate_sufficient_statistics(
            stats, obs, framelogprob, posteriors, fwdlattice, bwdlattice,
            params)
        if 'e' in params:
            for t, symbol in enumerate(obs):
                stats['obs'][:, symbol] += posteriors[t]

    def _do_mstep(self, stats, params, **kwargs):
        super(MultinomialHMM, self)._do_mstep(stats, params)
        if 'e' in params:
            self._set_emissionprob((stats['obs']
                                    / stats['obs'].sum(1)[:, np.newaxis]))


class GMMHMM(_BaseHMM):
    """Hidden Markov Model with Gaussin mixture emissions

    Attributes
    ----------
    n_components : int
        Number of states in the model.

    transmat : array, shape (`n_components`, `n_components`)
        Matrix of transition probabilities between states.

    startprob : array, shape ('n_components`,)
        Initial state occupation distribution.

    gmms : array of GMM objects, length `n_components`
        GMM emission distributions for each state.

    Examples
    --------
    >>> from sklearn.hmm import GMMHMM
    >>> GMMHMM(n_components=2, n_mix=10, covariance_type='diag')
    ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    GMMHMM(covariance_type=None,
        gmms=[GMM(covariance_type=None, min_covar=0.001, n_components=10, random_state=None,
      thresh=0.01), GMM(covariance_type=None, min_covar=0.001, n_components=10, random_state=None,
      thresh=0.01)],
        n_components=2, n_mix=10, startprob=None, startprob_prior=1.0,
        transmat=None, transmat_prior=1.0)

    See Also
    --------
    GaussianHMM : HMM with Gaussian emissions
    """

    def __init__(self, n_components=1, n_mix=1, startprob=None,
                 transmat=None, startprob_prior=None, transmat_prior=None,
                 gmms=None, covariance_type=None):
        """Create a hidden Markov model with GMM emissions.

        Parameters
        ----------
        n_components : int
            Number of states.
        """
        super(GMMHMM, self).__init__(n_components, startprob, transmat,
                                     startprob_prior=startprob_prior,
                                     transmat_prior=transmat_prior)

        # XXX: Hotfit for n_mix that is incompatible with the scikit's
        # BaseEstimator API
        self.n_mix = n_mix
        self._covariance_type = covariance_type
        if gmms is None:
            gmms = []
            for x in xrange(self.n_components):
                if covariance_type is None:
                    g = GMM(n_mix)
                else:
                    g = GMM(n_mix, covariance_type=covariance_type)
                gmms.append(g)
        self.gmms = gmms

    def _compute_log_likelihood(self, obs):
        return np.array([g.score(obs) for g in self.gmms]).T

    def _generate_sample_from_state(self, state, random_state=None):
        return self.gmms[state].sample(1, random_state=random_state).flatten()

    def _init(self, obs, params='stwmc'):
        super(GMMHMM, self)._init(obs, params=params)

        allobs = np.concatenate(obs, 0)
        for g in self.gmms:
            g.fit(allobs, n_iter=0, init_params=params)

    def _initialize_sufficient_statistics(self):
        stats = super(GMMHMM, self)._initialize_sufficient_statistics()
        stats['norm'] = [np.zeros(g.weights_.shape) for g in self.gmms]
        stats['means'] = [np.zeros(np.shape(g.means_)) for g in self.gmms]
        stats['covars'] = [np.zeros(np.shape(g.covars_)) for g in self.gmms]
        return stats

    def _accumulate_sufficient_statistics(self, stats, obs, framelogprob,
                                          posteriors, fwdlattice, bwdlattice,
                                          params):
        super(GMMHMM, self)._accumulate_sufficient_statistics(
            stats, obs, framelogprob, posteriors, fwdlattice, bwdlattice,
            params)

        for state, g in enumerate(self.gmms):
            _, lgmm_posteriors = g.eval(obs)
            lgmm_posteriors += np.log(posteriors[:, state][:, np.newaxis]
                                      + np.finfo(np.float).eps)
            gmm_posteriors = np.exp(lgmm_posteriors)
            tmp_gmm = GMM(g.n_components, covariance_type=g._covariance_type)
            n_features = g.means_.shape[1]
            tmp_gmm._set_covars(
                distribute_covar_matrix_to_match_covariance_type(
                    np.eye(n_features), g._covariance_type,
                    g.n_components))
            norm = tmp_gmm._do_mstep(obs, gmm_posteriors, params)

            if np.any(np.isnan(tmp_gmm.covars_)):
                raise ValueError

            stats['norm'][state] += norm
            if 'm' in params:
                stats['means'][state] += tmp_gmm.means_ * norm[:, np.newaxis]
            if 'c' in params:
                if tmp_gmm._covariance_type == 'tied':
                    stats['covars'][state] += tmp_gmm.covars_ * norm.sum()
                else:
                    cvnorm = np.copy(norm)
                    shape = np.ones(tmp_gmm.covars_.ndim)
                    shape[0] = np.shape(tmp_gmm.covars_)[0]
                    cvnorm.shape = shape
                    stats['covars'][state] += tmp_gmm.covars_ * cvnorm

    def _do_mstep(self, stats, params, covars_prior=1e-2, **kwargs):
        super(GMMHMM, self)._do_mstep(stats, params)
        # All that is left to do is to apply covars_prior to the
        # parameters updated in _accumulate_sufficient_statistics.
        for state, g in enumerate(self.gmms):
            n_features = g.means_.shape[1]
            norm = stats['norm'][state]
            if 'w' in params:
                g.weights_ = normalize(norm)
            if 'm' in params:
                g.means_ = stats['means'][state] / norm[:, np.newaxis]
            if 'c' in params:
                if g._covariance_type == 'tied':
                    g.covars_ = ((stats['covars'][state]
                                 + covars_prior * np.eye(n_features))
                                / norm.sum())
                else:
                    cvnorm = np.copy(norm)
                    shape = np.ones(g.covars_.ndim)
                    shape[0] = np.shape(g.covars_)[0]
                    cvnorm.shape = shape
                    if (g._covariance_type in ['spherical', 'diag']):
                        g.covars_ = (stats['covars'][state]
                                    + covars_prior) / cvnorm
                    elif g._covariance_type == 'full':
                        eye = np.eye(n_features)
                        g.covars_ = ((stats['covars'][state]
                                     + covars_prior * eye[np.newaxis])
                                    / cvnorm)
