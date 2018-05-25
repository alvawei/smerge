""" Non-negative matrix factorization
"""
# Author: Chih-Jen Lin, National Taiwan University
# Python/numpy translation: Anthony Di Franco
# scikit.learn integration: Vlad Niculae
# License: BSD


from __future__ import division
import warnings

import numpy as np
from .base import BaseEstimator, TransformerMixin
from .utils.extmath import fast_svd

_pos_ = lambda x: (x >= 0) * x
_neg_ = lambda x: (x < 0) * (-x)
norm = lambda x: np.sqrt(np.dot(x.flatten().T, x.flatten()))


def _sparseness_(x):
    """
        Default: None
    ----------
    -------
    """


























