"""
Base IO code for all datasets
"""

# Copyright (c) 2007 David Cournapeau <cournape@gmail.com>
#               2010 Fabian Pedregosa <fabian.pedregosa@inria.fr>
#               2010 Olivier Grisel <olivier.grisel@ensta.org>
# License: Simplified BSD

import csv
import shutil
import textwrap
from os import environ
from os.path import dirname
from os.path import join
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os import listdir
from os import makedirs

import numpy as np

from ..utils import check_random_state


def load_boston():
    """Load and return the boston house-prices dataset (regression).

    Returns
    -------
    data : Bunch
        Dictionary-like object, the interesting attributes are:
        'data', the data to learn, 'target', the classification labels,
        'target_names', the meaning of the labels, and 'DESCR', the
        full description of the dataset.

    Example
    -------
    >>> from scikits.learn.datasets import load_boston
    >>> data = load_boston()

    """

    module_path = dirname(__file__)
    data_file = csv.reader(open(join(module_path, 'data',
                                     'boston_house_prices.csv')))
    fdescr = open(join(module_path, 'descr', 'boston_house_prices.rst'))
    temp = data_file.next()
    n_samples = int(temp[0])
    n_features = int(temp[1])
    data = np.empty((n_samples, n_features))
    target = np.empty((n_samples,))
    temp = data_file.next()  # names of features
    feature_names = np.array(temp)
    for i, d in enumerate(data_file):
        data[i] = np.asanyarray(d[:-1], dtype=np.float)
        target[i] = np.asanyarray(d[-1], dtype=np.float)

    return Bunch(data=data, target=target,
                 feature_names=feature_names,
                 DESCR=fdescr.read())
for function, filename in ((load_diabetes, 'diabetes.rst'),
                           (load_iris, 'iris.rst'),
                           (load_linnerud, 'linnerud.rst'),
                           (load_digits, 'digits.rst')):
    #try:
        _add_notes(function, filename)
    #except:
    #    pass
def load_iris():
    """Load and return the iris dataset (classification).

    Returns
    -------
    data : Bunch
        Dictionnary-like object, the interesting attributes are:
        'data', the data to learn, 'target', the classification labels,
        'target_names', the meaning of the labels, and 'DESCR', the
        full description of the dataset.

    Example
    -------
    Let's say you are interested in the samples 10, 25, and 50, and want to
    know their class name.

    >>> from scikits.learn.datasets import load_iris
    >>> data = load_iris()
    >>> data.target[[10, 25, 50]]
    array([0, 0, 1])
    >>> list(data.target_names)
    ['setosa', 'versicolor', 'virginica']

    """

    module_path = dirname(__file__)
    data_file = csv.reader(open(join(module_path, 'data', 'iris.csv')))
    fdescr = open(join(module_path, 'descr', 'iris.rst'))
    temp = data_file.next()
    n_samples = int(temp[0])
    n_features = int(temp[1])
    target_names = np.array(temp[2:])
    data = np.empty((n_samples, n_features))
    target = np.empty((n_samples,), dtype=np.int)
    for i, ir in enumerate(data_file):
        data[i] = np.asanyarray(ir[:-1], dtype=np.float)
        target[i] = np.asanyarray(ir[-1], dtype=np.int)

    return Bunch(data=data, target=target, target_names=target_names,
                 DESCR=fdescr.read(),
                 feature_names=['sepal length (cm)', 'sepal width (cm)',
                                'petal length (cm)', 'petal width (cm)'])


def load_digits(n_class=10):
    """Load and return the digits dataset (classification).

    Parameters
    ----------
    n_class : integer, between 0 and 10
        Number of classes to return, defaults to 10

    Returns
    -------
    data : Bunch
        Dictionary-like object, the interesting attributes are:
        'data', the data to learn, `images`, the images corresponding
        to each sample, 'target', the classification labels for each
        sample, 'target_names', the meaning of the labels, and 'DESCR',
        the full description of the dataset.

    Example
    -------
    To load the data and visualize the images::

        import pylab as pl
        digits = datasets.load_digits()
        pl.gray()
        # Visualize the first image:
        pl.matshow(digits.raw_data[0])

    """

    module_path = dirname(__file__)
    data = np.loadtxt(join(module_path, 'data', 'digits.csv.gz'),
                      delimiter=',')
    descr = open(join(module_path, 'descr', 'digits.rst')).read()
    target = data[:, -1]
    flat_data = data[:, :-1]
    images = flat_data.view()
    images.shape = (-1, 8, 8)

    if n_class < 10:
        idx = target < n_class
        flat_data, target = flat_data[idx], target[idx]
        images = images[idx]

    return Bunch(data=flat_data,
                 target=target.astype(np.int),
                 target_names=np.arange(10),
                 images=images,
                 DESCR=descr)


def load_diabetes():
    """ Load and return the diabetes dataset (regression).

    Returns
    -------
    data : Bunch
        Dictionnary-like object, the interesting attributes are:
        'data', the data to learn and 'target', the labels for each
        sample.


    """
    base_dir = join(dirname(__file__), 'data')
    data = np.loadtxt(join(base_dir, 'diabetes_data.csv.gz'))
    target = np.loadtxt(join(base_dir, 'diabetes_target.csv.gz'))
    return Bunch(data=data, target=target)


def load_linnerud():
    """ Load and return the linnerud dataset (multivariate regression).

    Returns
    -------
    data : Bunch
        Dictionnary-like object, the interesting attributes are:
        'data_exercise' and 'data_physiological', the two multivariate
        datasets, as well as 'header_exercise' and
        'header_physiological', the corresponding headers.

    """
    base_dir = join(dirname(__file__), 'data/')
    # Read data
    data_exercise = np.loadtxt(base_dir + 'linnerud_exercise.csv', skiprows=1)
    data_physiological = np.loadtxt(base_dir + 'linnerud_physiological.csv',
                                    skiprows=1)
    # Read header
    f = open(base_dir + 'linnerud_exercise.csv')
    header_exercise = f.readline().split()
    f.close()
    f = open(base_dir + 'linnerud_physiological.csv')
    header_physiological = f.readline().split()
    f.close()
    fdescr = open(dirname(__file__) + '/descr/linnerud.rst')
    return Bunch(data_exercise=data_exercise, header_exercise=header_exercise,
                 data_physiological=data_physiological,
                 header_physiological=header_physiological,
                 DESCR=fdescr.read())



