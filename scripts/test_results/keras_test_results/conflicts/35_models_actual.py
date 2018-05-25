import theano
import theano.tensor as T
import numpy as np

import optimizers
import objectives
import time, copy
from utils.generic_utils import Progbar

def standardize_y(y):
    if not hasattr(y, 'shape'):
        y = np.asarray(y)
    y = np.asarray(y)
    if len(y.shape) == 1:
        y = np.reshape(y, (len(y), 1))
    return y

class Sequential(object):
    def __init__(self):
        self.layers = []
        self.params = []
    def add(self, layer):
        self.layers.append(layer)
        if len(self.layers) > 1:
            self.layers[-1].connect(self.layers[-2])
        self.params += [p for p in layer.params]
    def predict_classes(self, X, batch_size=128, verbose=1):
        proba = self.predict_proba(X, batch_size=batch_size, verbose=verbose)
        if self.class_mode == "categorical":
            return proba.argmax(axis=-1)
            return proba.argmax(axis=-1)
        else:
        else:
            return (proba>0.5).astype('int32')
            return (proba>0.5).astype('int32')
        else:
<<<<<<< REMOTE
return self._train(X, y)
=======
progbar.update(batch_end, [('loss', loss), ('val. loss', self.test(X_val, y_val))])
>>>>>>> LOCAL
            return (proba>0.5).astype('int32')










        


                
            






