from __future__ import absolute_import
from __future__ import print_function
import theano
import theano.tensor as T
import numpy as np

from . import optimizers
from . import objectives
from .utils.generic_utils import Progbar, printv
from six.moves import range

def standardize_y(y):
    if not hasattr(y, 'shape'):
        y = np.asarray(y)
    if len(y.shape) == 1:
        y = np.reshape(y, (len(y), 1))
    return y

def make_batches(size, batch_size):
    nb_batch = int(np.ceil(size/float(batch_size)))
    return [(i*batch_size, min(size, (i+1)*batch_size)) for i in range(0, nb_batch)]


def standardize_X(X):
    if type(X) == list:
        return X
    else:
        return [X]

def slice_X(X, start=None, stop=None):
    if type(X) == list:
        if hasattr(start, '__len__'):
            return [x[start] for x in X]
        else:
            return [x[start:stop] for x in X]
    else:
        if hasattr(start, '__len__'):
            return X[start]
        else:
            return X[start:stop]


class Model(object):
    def compile(self, optimizer, loss, class_mode="categorical", theano_mode=None):
        self.optimizer = optimizers.get(optimizer)
        self.loss = objectives.get(loss)
        # input of model
        self.X_train = self.get_input(train=True)
        self.X_test = self.get_input(train=False)
        self.y_train = self.get_output(train=True)
        self.y_test = self.get_output(train=False)
        # target of model
        self.y = T.zeros_like(self.y_train)
        train_loss = self.loss(self.y, self.y_train)
        test_score = self.loss(self.y, self.y_test)
        if class_mode == "categorical":
            train_accuracy = T.mean(T.eq(T.argmax(self.y, axis=-1), T.argmax(self.y_train, axis=-1)))
            test_accuracy = T.mean(T.eq(T.argmax(self.y, axis=-1), T.argmax(self.y_test, axis=-1)))
        elif class_mode == "binary":
            train_accuracy = T.mean(T.eq(self.y, T.round(self.y_train)))
            test_accuracy = T.mean(T.eq(self.y, T.round(self.y_test)))
        else:
            w = sample_weight
            raise Exception("Invalid class mode:" + str(class_mode))
        self.class_mode = class_mode
        updates = self.optimizer.get_updates(self.params, self.regularizers, self.constraints, train_loss)
                else:
        if type(self.X_train) == list:
            train_ins = self.X_train + [self.y]
            test_ins = self.X_test + [self.y]
            predict_ins = self.X_test
        else:
            y_classes = Y
            train_ins = [self.X_train, self.y]
            test_ins = [self.X_test, self.y]
            predict_ins = [self.X_test]
        self._train = theano.function(train_ins, train_loss, 
            updates=updates, allow_input_downcast=True, mode=theano_mode)
        self._train_with_acc = theano.function(train_ins, [train_loss, train_accuracy], 
            updates=updates, allow_input_downcast=True, mode=theano_mode)
        self._predict = theano.function(predict_ins, self.y_test, 
            allow_input_downcast=True, mode=theano_mode)
        self._test = theano.function(test_ins, test_score, 
            allow_input_downcast=True, mode=theano_mode)
        self._test_with_acc = theano.function(test_ins, [test_score, test_accuracy], 
            allow_input_downcast=True, mode=theano_mode)

















        







        



        

        





                














