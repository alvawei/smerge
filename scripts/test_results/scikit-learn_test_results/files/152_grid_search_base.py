import numpy as np

from joblib import Parallel, delayed

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


def grid(**kwargs):
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
        >>> list(grid(a=[1, 2], b=[True, False]))
        [{'a': 1, 'b': True}, {'a': 1, 'b': False}, {'a': 2, 'b': True}, {'a': 2, 'b': False}]
    """
    keys = kwargs.keys()
    for v in product(*kwargs.values()):
        params = dict(zip(keys,v))
        yield params


def fit_grid_point(X, y, klass, orignal_params, clf_params, cross_val_factory,
                                        loss_func, **fit_params):
    """Run fit on one set of parameters
    Returns the score and the instance of the classifier
    """
    params = orignal_params.copy()
    params.update(clf_params)
    n_samples, n_features = X.shape
    clf = klass(**params)
    cv = cross_val_factory(n_samples)
    y_pred = list()
    y_true = list()
    for train, test in cv:
        clf.fit(X[train], y[train], **fit_params)
        y_pred.append(clf.predict(X[test]))
        y_true.append(y[test])

    y_true = np.concatenate(y_true)
    y_pred = np.concatenate(y_pred)

    score = loss_func(y_true, y_pred)
    return clf, score


class GridSearchCV(object):
    """
    Object to run a grid search on the parameters of a classifier.

    Important memmbers are fit, predict.

    GridSearchCV implements a "fit" method and a "predict" method like
    any classifier except that the parameters of the classifier
    used to predict is optimized by cross-validation

    Parameters
    ---------
    estimator: object type that implements the "fit" and "predict" methods
        A object of that type is instanciated for each grid point

    param_grid: dict
        a dictionary of parameters that are used the generate the grid

    cross_val_factory : a generator to run crossvalidation

    loss_func : function that takes 2 arguments and compares them in
        order to evaluate the performance of prediciton (small is good)

    n_jobs : int
        number of jobs to run in parallel (default 1)

    Optional Parameters
    -------------------

    Members
    -------

    Examples
    --------
    >>> import numpy as np
    >>> from scikits.learn.cross_val import LeaveOneOut
    >>> from scikits.learn.svm import SVC
    >>> X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
    >>> y = np.array([1, 1, 2, 2])
    >>> parameters = {'kernel':('linear', 'rbf'), 'C':[1, 10]}
    >>> def loss_func(y1, y2):
    ...     return np.mean(y1 != y2)
    >>> svc = SVC()
    >>> clf = GridSearchCV(svc, parameters, LeaveOneOut, loss_func, n_jobs=1)
    >>> print clf.fit(X, y).predict([[-0.8, -1]])
    [ 1.]
    """
    # XXX: cross_val_factory should have a default
    def __init__(self, estimator, param_grid, cross_val_factory, loss_func,
                        fit_params={}, n_jobs=1):
        assert hasattr(estimator, 'fit') and hasattr(estimator, 'predict'), (
            "estimator should a be an estimator implementing 'fit' and " 
            "'predict' methods, %s (type %s) was passed" % (clf, type(clf))
            )
        self.estimator = estimator
        self.param_grid = param_grid
        self.cross_val_factory = cross_val_factory
        self.loss_func = loss_func
        self.n_jobs = n_jobs
        self.fit_params = fit_params


    def fit(self, X, y, **kw):
        """Run fit with all sets of parameters
        Returns the best classifier
        """

        g = grid(**self.param_grid)
        klass = self.estimator.__class__
        orignal_params = self.estimator._get_params()
        out = Parallel(n_jobs=self.n_jobs)(
            delayed(fit_grid_point)(X, y, klass, orignal_params, clf_params,
                    self.cross_val_factory,
                    self.loss_func, **self.fit_params) for clf_params in g)

        # Out is a list of pairs: estimator, score
        key = lambda pair: pair[1]
        best_estimator = min(out, key=key)[0]

        self.best_estimator = best_estimator
        self.predict = best_estimator.predict

        return self


if __name__ == '__main__':

    from scikits.learn.cross_val import LeaveOneOut
    from scikits.learn.svm import SVC
    X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
    y = np.array([1, 1, 2, 2])
    svc = SVC(kernel='linear') 
    def loss_func(y1, y2):
        return np.mean(y1 != y2)
    clf = GridSearchCV(svc, {'C':[1, 10]}, LeaveOneOut, loss_func, n_jobs=2)
    print clf.fit(X, y).predict([[-0.8, -1]])
