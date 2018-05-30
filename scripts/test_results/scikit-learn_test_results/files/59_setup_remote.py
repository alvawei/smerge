from os.path import join
import warnings


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info, BlasNotFoundError

    config = Configuration('sklearn', parent_package, top_path)

    config.add_subpackage('check_build')
    config.add_subpackage('svm')
    config.add_subpackage('datasets')
    config.add_subpackage('datasets/tests')
    config.add_subpackage('feature_extraction')
    config.add_subpackage('feature_extraction/tests')
    config.add_subpackage('cluster')
    config.add_subpackage('cluster/tests')
    config.add_subpackage('covariance')
    config.add_subpackage('covariance/tests')
    config.add_subpackage('decomposition')
    config.add_subpackage('decomposition/tests')
    config.add_subpackage('feature_selection')
    config.add_subpackage('feature_selection/tests')
    config.add_subpackage('preprocessing')
    config.add_subpackage('utils')
    config.add_subpackage('utils/tests')
    config.add_subpackage('externals')
    config.add_subpackage('mixture')
    config.add_subpackage('mixture/tests')
    config.add_subpackage('gaussian_process')
    config.add_subpackage('gaussian_process/tests')
    config.add_subpackage('neighbors')
    config.add_subpackage('manifold')
    config.add_subpackage('metrics')
    config.add_subpackage('metrics/tests')
    config.add_subpackage('metrics/cluster')
    config.add_subpackage('metrics/cluster/tests')

    # some libs needs cblas, fortran-compiled BLAS will not be sufficient
    blas_info = get_info('blas_opt', 0)
    if (not blas_info) or (
        ('NO_ATLAS_INFO', 1) in blas_info.get('define_macros', [])):
        config.add_library('cblas',
                           sources=[join('src', 'cblas', '*.c')])
        warnings.warn(BlasNotFoundError.__doc__)

    # the following packages depend on cblas, so they have to be build
    # after the above.
    config.add_subpackage('linear_model')
    config.add_subpackage('utils')

    # add the test directory
    config.add_subpackage('tests')

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
