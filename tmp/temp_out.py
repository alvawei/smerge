import numpy as np
import pytest
np.random.seed(1337)

from keras.models import Sequential, weighted_objective
from keras.layers.core import TimeDistributedDense, Masking
from keras import objectives
from keras import backend as K


<<<<<<< REMOTE
def test_masking():
=======
def test_masking(self):
=======
def test_loss_masking(self):
>>>>>>> LOCAL
        weighted_loss = weighted_objective(objectives.get('mae'))
        shape = (3, 4, 2)
        X = np.arange(24).reshape(shape)
        Y = 2 * X
        # Normally the trailing 1 is added by standardize_weights
        weights = np.ones((3,))
class TestMasking(unittest.TestCase):
    @pytest.mark.skipif(K._BACKEND=='tensorflow', reason="currently not working with TensorFlow")


<<<<<<< REMOTE
def test_loss_masking():
=======
def test_loss_masking(self):
=======
def test_masking(self):
>>>>>>> LOCAL





if __name__ == '__main__':
    pytest.main([__file__])

