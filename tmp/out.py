import numpy as np
import pytest
np.random.seed(1337)

from keras.models import Sequential, weighted_objective
from keras.layers.core import TimeDistributedDense, Masking
from keras import objectives
from keras import backend as K


    def test_masking(self):
        weighted_loss = weighted_objective(objectives.get('mae'))
        shape = (3, 4, 2)
        X = np.arange(24).reshape(shape)
        Y = 2 * X
        # Normally the trailing 1 is added by standardize_weights
        weights = np.ones((3,))
        mask = np.ones((3, 4))
        mask[1, 0] = 0
        out = K.eval(weighted_loss(K.variable(X),
                                   K.variable(Y),
                                   K.variable(weights),
                                   K.variable(mask)))
        print(out)
class TestMasking(unittest.TestCase):
    @pytest.mark.skipif(K._BACKEND=='tensorflow', reason="currently not working with TensorFlow")


    def test_loss_masking(self):




if __name__ == '__main__':


