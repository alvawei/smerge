"""
Machine Learning module in python
=================================

scikits.learn is a Python module integrating classical machine
learning algorithms in the tightly-knit world of scientific Python
packages (numpy, scipy, matplotlib).

It aims to provide simple and efficient solutions to learning problems
that are accessible to everybody and reusable in various contexts:
machine-learning as a versatile tool for science and engineering.

See http://scikit-learn.sourceforge.net for complete documentation.
"""

try:
    from . import check_build
except ImportError:
    raise ImportError("Please do not forget to run `make` first")

from .base import clone

from . import mixture

try:
    from numpy.testing import nosetester

    class NoseTester(nosetester.NoseTester):
        """ Subclass numpy's NoseTester to add doctests by default
        """

        def test(self, label='fast', verbose=1, extra_argv=['--exe'],
                        doctests=True, coverage=False):
            return super(NoseTester, self).test(label=label, verbose=verbose,
                                    extra_argv=extra_argv,
                                    doctests=doctests, coverage=coverage)

    test = NoseTester().test
    del nosetester
except:
    pass


__all__ = ['check_build', 'cross_val', 'ball_tree', 'cluster', 'covariance',
           'datasets', 'decomposition', 'feature_extraction',
           'feature_selection',
           'gaussian_process', 'grid_search', 'hmm', 'lda', 'linear_model',
           'metrics', 'mixture', 'naive_bayes', 'neighbors', 'pipeline',
           'preprocessing', 'qda', 'svm', 'test', 'clone', 'pls', 'tree']

__version__ = '0.9-git'
