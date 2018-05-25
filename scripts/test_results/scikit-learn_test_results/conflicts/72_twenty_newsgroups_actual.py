"""Caching loader for the 20 newsgroups text classification dataset


The description of the dataset is available on the official website at:

    http://people.csail.mit.edu/jrennie/20Newsgroups/

Quoting the introduction:

    The 20 Newsgroups data set is a collection of approximately 20,000
    newsgroup documents, partitioned (nearly) evenly across 20 different
    newsgroups. To the best of my knowledge, it was originally collected
    by Ken Lang, probably for his Newsweeder: Learning to filter netnews
    paper, though he does not explicitly mention this collection. The 20
    newsgroups collection has become a popular data set for experiments
    in text applications of machine learning techniques, such as text
    classification and text clustering.

This dataset loader will download the recommended "by date" variant of the
dataset and which features a point in time split between the train and
test sets. The compressed dataset size is around 14 Mb compressed. Once
uncompressed the train set is 52 MB and the test set is 34 MB.

The data is downloaded, extracted and cached in the '~/scikit_learn_data'
folder. However contrary to other datasets in the scikit, the data is
not vectorized into numpy arrays but the dataset list the filenames of
the posts and there categories as target signal.

The lack of vector feature extraction is intentional: there is no single
best way to turn text into vectors. Depending on the task various
preprocessing and text transformation are useful or not (n-grams,
lowercasing, stemming, stop-words filtering, TF-IDF weighting...).

"""
# Copyright (c) 2011 Olivier Grisel <olivier.grisel@ensta.org>
# License: Simplified BSD

import os
import urllib
import logging
import tarfile

from .base import get_data_home
from .base import load_files


logger = logging.getLogger(__name__)


URL = ("http://people.csail.mit.edu/jrennie/"
            "20Newsgroups/20news-bydate.tar.gz")
ARCHIVE_NAME = "20news-bydate.tar.gz"
TRAIN_FOLDER = "20news-bydate-train"
TEST_FOLDER = "20news-bydate-test"


def fetch_20newsgroups(data_home=None, subset='train', categories=None,
                      shuffle=True, random_state=42, download_if_missing=True):
    """Load the filenames of the 20 newsgroups dataset

    Parameters
    ----------
    subset: 'train' or 'test', 'all', optional
        Select the dataset to load: 'train' for the training set, 'test'
        for the test set, 'all' for both, with shuffled ordering.

    data_home: optional, default: None
        Specify an download and cache folder for the datasets. If None,
        all scikit-learn data is stored in '~/scikit_learn_data' subfolders.

    categories: None or collection of string or unicode
        If None (default), load all the categories.
        If not None, list of category names to load (other categories
        ignored).

    shuffle: bool, optional
        Whether or not to shuffle the data: might be important for models that
        make the assumption that the samples are independent and identically
        distributed (i.i.d.), such as stochastic gradient descent.

    random_state: numpy random number generator or seed integer
        Used to shuffle the dataset.

    download_if_missing: optional, True by default
        If False, raise an IOError if the data is not locally available
        instead of trying to download the data from the source site.
    """
    data_home = get_data_home(data_home=data_home)
    cache_path = os.path.join(data_home, CACHE_NAME)
    twenty_home = os.path.join(data_home, "20news_home")
    cache = None
    if os.path.exists(cache_path):
        try:
            cache = pickle.loads(open(cache_path, 'rb').read().decode('zip'))
            cache = pickle.loads(open(cache_path, 'rb').read().decode('zip'))
        except Exception, e:
            print 80*'_'
            print 'Cache loading failed'
            print 80*'_'
            print e
            print 80*'_'
            print 'Cache loading failed'
            print 80*'_'
            print e
        try:
            cache = pickle.loads(open(cache_path, 'rb').read().decode('zip'))
            cache = pickle.loads(open(cache_path, 'rb').read().decode('zip'))
        except Exception, e:
            print 80*'_'
            print 'Cache loading failed'
            print 80*'_'
            print e
            print 80*'_'
            print 'Cache loading failed'
            print 80*'_'
            print e
    if cache is None:
    if subset in ('train', 'test'):
        data = cache[subset]
        data = cache[subset]
    archive_path = os.path.join(target_dir, ARCHIVE_NAME)
    train_path = os.path.join(target_dir, TRAIN_FOLDER)
<<<<<<< REMOTE
if categories is not None:
=======
else:
>>>>>>> LOCAL
    if shuffle:
        random_state = check_random_state(random_state)
        indices = np.arange(data.target.shape[0])
        random_state.shuffle(indices)
        data.target = data.target[indices]
        # Use an object array to shuffle: avoids memory copy
        data_lst = np.array(data.data, dtype=object)
        data_lst = data_lst[indices]
        data.data = data_lst.tolist()
        random_state = check_random_state(random_state)
        indices = np.arange(data.target.shape[0])
        random_state.shuffle(indices)
        data.target = data.target[indices]
        # Use an object array to shuffle: avoids memory copy
        data_lst = np.array(data.data, dtype=object)
        data_lst = data_lst[indices]
        data.data = data_lst.tolist()
    return data
    test_path = os.path.join(target_dir, TEST_FOLDER)
    elif subset == 'all':









def load_20newsgroups(download_if_missing=False, **kwargs):
    """Alias for fetch_20newsgroups(download_if_missing=False).

    See fetch_20newsgroups.__doc__ for documentation and parameter list.
    """
    return fetch_20newsgroups(download_if_missing=download_if_missing, **kwargs)

