# Copyright (c) 2010 Olivier Grisel <olivier.grisel@ensta.org>
# License: Simplified BSD
"""Glue code to load http://mlcomp.org data as a scikit.learn dataset"""

import os
import numpy as np
from scikits.learn.feature_extraction.text import HashingVectorizer
from scikits.learn.feature_extraction.text import SparseHashingVectorizer


def _load_document_classification(dataset_path, metadata, set_=None):
    dataset_path = os.path.join(dataset_path, set_)






LOADERS = {
    'DocumentClassification': _load_document_classification,
    # TODO: implement the remaining domain formats
}







