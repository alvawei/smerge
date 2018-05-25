"""
Generalized linear models
=========================

<<<<<<< HEAD
scikits.learn.glm is a module to fit genelarized linear models.
It includes Ridge regression, Bayesian Regression, Lasso and
Elastic Net estimators computed with Least Angle Regression
and coordinate descent.

"""

from .lars import LARS, LassoLARS, lars_path, LeastAngleRegression
=======
from .base import LinearRegression
from .lars import LARS, LassoLARS, LeastAngleRegression
>>>>>>> remote
from .coordinate_descent import Lasso, ElasticNet, LassoCV, ElasticNetCV
from .bayes import Ridge, BayesianRidge, ARDRegression

