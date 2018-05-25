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


class Bunch(dict):
    """ Container object for datasets: dictionnary-like object that
        exposes its keys as attributes.
    """

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__ = self


def get_data_home(data_home=None):
    """Return the path of the scikit-learn data dir

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'scikit_learn_data'
    in the user home folder.

    Alternatively, it can be set by the 'SCIKIT_LEARN_DATA' environment
    variable or programatically by giving an explit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.
    """
    if data_home is None:
        data_home = environ.get('SCIKIT_LEARN_DATA',
                               join('~', 'scikit_learn_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home


def clear_data_home(data_home=None):
    """Delete all the content of the data home cache"""
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)


def load_files(container_path, description=None, categories=None,
               load_content=True, shuffle=True, random_state=42):
    """Load text files with categories as subfolder names

    Individual samples are assumed to be files stored a two levels folder
    structure such as the following:

        container_folder/
            category_1_folder/
                file_1.txt
                file_2.txt
                ...
                file_42.txt
            category_2_folder/
                file_43.txt
                file_44.txt
                ...

    The folder names are used has supervised signal label names. The indivial
    file names are not important.

    This function does not try to extract features into a numpy array or
    scipy sparse matrix. In addition, if load_content is false it
    does not try to load the files in memory.

    To use utf-8 text files in a scikit-learn classification or clustering
    algorithm you will first need to use the `scikits.learn.features.text`
    module to build a feature extraction transformer that suits your
    problem.

    Similar feature extractors should be build for other kind of unstructured
    data input such as images, audio, video, ...

    Parameters
    ----------

    container_path : string or unicode
        Path to the main folder holding one subfolder per category

    description: string or unicode
        A paragraph describing the characteristic of the dataset: its source,
        reference, etc.

    categories : None or collection of string or unicode
        If None (default), load all the categories.
        If not None, list of category names to load (other categories ignored).

    load_content : boolean
        Whether to load or not the content of the different files. If
        true a 'data' attribute containing the text information is present
        in the data structure returned. If not, a filenames attribute
        gives the path to the files.

    shuffle : bool, optional
        Whether or not to shuffle the data: might be important for models that
        make the assumption that the samples are independent and identically
        distributed (i.i.d.), such as stochastic gradient descent.

    random_state : numpy random number generator or seed integer, optional
        Used to shuffle the dataset.

    Returns
    -------
    data : Bunch
        Dictionary-like object, the interesting attributes are: either
        data, the raw text data to learn, or 'filenames', the files
        holding it, 'target', the classification labels (integer index),
        'target_names', the meaning of the labels, and 'DESCR', the full
        description of the dataset.
    """
    target = []
    target_names = []
    filenames = []

    folders = [f for f in sorted(listdir(container_path))
               if isdir(join(container_path, f))]

    if categories is not None:
        folders = [f for f in folders if f in categories]

    for label, folder in enumerate(folders):
        target_names.append(folder)
        folder_path = join(container_path, folder)
        documents = [join(folder_path, d)
                     for d in sorted(listdir(folder_path))]
        target.extend(len(documents) * [label])
        filenames.extend(documents)

    # convert to array for fancy indexing
    filenames = np.array(filenames)
    target = np.array(target)

    if shuffle:
        random_state = check_random_state(random_state)
        indices = np.arange(filenames.shape[0])
        random_state.shuffle(indices)
        filenames = filenames[indices]
        target = target[indices]

    if load_content:
        data = [open(filename).read() for filename in filenames]
        return Bunch(data=data,
                     target_names=target_names,
                     target=target,
                     DESCR=description)

    return Bunch(filenames=filenames,
                 target_names=target_names,
                 target=target,
                 DESCR=description)


###############################################################################

def load_iris():
    """Load and return the iris dataset (classification).

    Returns
    -------
    data : Bunch
        Dictionary-like object, the interesting attributes are:
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

    return Bunch(data=flat_data, target=target.astype(np.int),
                 target_names=np.arange(10),
                 images=images,
                 DESCR=descr)


def load_diabetes():
    """ Load and return the diabetes dataset (regression).

    Returns
    -------
    data : Bunch
        Dictionary-like object, the interesting attributes are:
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
        Dictionary-like object, the interesting attributes are:
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

def load_boston():
    """load the boston house prices dataset and returns it.

def load_boston():
    """Load the Boston house prices dataset and return it.

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
