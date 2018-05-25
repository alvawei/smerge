"""
Tune the parameters of an estimator by cross-validation.
"""

# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>,
#         Gael Varoquaux    <gael.varoquaux@normalesup.org>
# License: BSD Style.

import copy

from .externals.joblib import Parallel, delayed
from .cross_val import KFold, StratifiedKFold

try:
    from itertools import product
except:
    def product(*args, **kwds):
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)


def iter_grid(param_grid):
    """ Generators on the combination of the various parameter lists given.

        Parameters
        -----------
        kwargs: keyword arguments, lists
            Each keyword argument must be a list of values that should
            be explored.

        Returns
        --------
        params: dictionary
            Dictionnary with the input parameters taking the various
            values succesively.

        Examples
        ---------
        >>> from scikits.learn.grid_search import iter_grid
        >>> param_grid = {'a':[1, 2], 'b':[True, False]}
        >>> list(iter_grid(param_grid))
        [{'a': 1, 'b': True}, {'a': 1, 'b': False}, {'a': 2, 'b': True}, {'a': 2, 'b': False}]

    """
    if hasattr(param_grid, 'has_key'):
        param_grid = [param_grid]
    for p in param_grid:
        for v in product(*values):
            params = dict(zip(keys, v))
            yield params


def fit_grid_point(X, y, base_clf, clf_params, cv, loss_func, iid,
                   **fit_params):
    """Run fit on one set of parameters
    Returns the score and the instance of the classifier
    """
    # update parameters of the classifier after a copy of its base structure
    clf = copy.deepcopy(base_clf)
    clf._set_params(**clf_params)
    score = 0.
    for train, test in cv:
        if isinstance(X, list) or isinstance(X, tuple):
            X_train = [X[i] for i, cond in enumerate(train) if cond]
            X_test = [X[i] for i, cond in enumerate(test) if cond]
            X_train = [X[i] for i, cond in enumerate(train) if cond]
            X_test = [X[i] for i, cond in enumerate(test) if cond]
        clf.fit(X_train, y[train], **fit_params)
            X_test = X[test]
        y_test = y[test]
        if loss_func is not None:
            y_pred = clf.predict(X_test)
            this_score = -loss_func(y_test, y_pred)
        else:
            X_train = X[train]
        if iid:
            this_score *= len(y_test)
            n_test_samples += len(y_test)
        score += this_score
    



################################################################################
















        




if __name__ == '__main__':
    from scikits.learn.svm import SVC
    from scikits.learn import datasets
    iris = datasets.load_iris()
    # Add the noisy data to the informative features
    X = iris.data
    y = iris.target
    svc = SVC(kernel='linear')
    clf = GridSearchCV(svc, {'C':[1, 10]}, n_jobs=1)
    print clf.fit(X, y).predict([[-0.8, -1]])




