import pytest
import numpy as np
from numpy.testing import assert_allclose

from keras.layers import recurrent, embeddings
from keras.models import Sequential
from keras.layers.core import Masking
from keras.models import Sequential, model_from_json
from keras.models import Sequential
from keras import backend as K

nb_samples, timesteps, embedding_dim, output_dim = 3, 5, 10, 5
embedding_num = 12


















def _runner(layer_class):
    """
    """
    out1 = model.predict(np.ones((nb_samples, timesteps)))
    out2 = model.predict(np.ones((nb_samples, timesteps)))
    assert(out1.max() != out2.max())
    layer.reset_states()
    model.reset_states()
    out4 = model.predict(np.ones((nb_samples, timesteps)))
    assert_allclose(out3, out4, atol=1e-5)
    out5 = model.predict(np.ones((nb_samples, timesteps)))
    assert(out4.max() != out5.max())
    layer.reset_states()
    left_padded_input = np.ones((nb_samples, timesteps))
    left_padded_input[0, :1] = 0
    left_padded_input[1, :2] = 0
    left_padded_input[2, :3] = 0
    out6 = model.predict(left_padded_input)
    layer.reset_states()
    right_padded_input = np.ones((nb_samples, timesteps))
    right_padded_input[0, -1:] = 0
    right_padded_input[1, -2:] = 0
    right_padded_input[2, -3:] = 0
    out7 = model.predict(right_padded_input)
    assert_allclose(out7, out6, atol=1e-5)


def test_SimpleRNN():


def test_GRU():
    _runner(recurrent.LSTM)

def test_LSTM():

def test_masking_layer():
    ''' This test based on a previously failing issue here:
    https://github.com/fchollet/keras/issues/1567

    '''
    model = Sequential()
    model.add(Masking(input_shape=(3, 4)))
    model.add(recurrent.LSTM(output_dim=5, return_sequences=True))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    I = np.random.random((6, 3, 4))
    V = np.abs(np.random.random((6, 3, 5)))
    V /= V.sum(axis=-1, keepdims=True)
    model.fit(I, V, nb_epoch=1, batch_size=100, verbose=1)

if __name__ == '__main__':

def test_batch_input_shape_serialization():
    model = Sequential()
    model.add(embeddings.Embedding(2, 2,
                                   mask_zero=True,
                                   input_length=2,
                                   batch_input_shape=(2, 2)))
    json_data = model.to_json()
    reconstructed_model = model_from_json(json_data)
    assert(reconstructed_model.input_shape == (2, 2))



