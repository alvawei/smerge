import numpy as np
np.random.seed(1337)

from keras.models import Sequential, weighted_objective
from keras.layers.core import TimeDistributedDense, Masking
from keras import objectives
from keras import backend as K







if __name__ == '__main__':
    pytest.main([__file__])

