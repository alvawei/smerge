import pytest
import numpy as np
from numpy.testing import assert_allclose

from keras.layers import recurrent, embeddings
from keras import backend as K
from keras.layers.core import Masking
from keras.models import Sequential, model_from_json
from keras.models import Sequential

nb_samples, timesteps, embedding_dim, output_dim = 3, 5, 10, 5
embedding_num = 12


def _runner(layer_class):
    """
    All the recurrent layers share the same interface,
    so we can run through them with a single function.
    """
    for ret_seq in [True, False]:
        layer = layer_class(output_dim, return_sequences=ret_seq,
                            weights=None, input_shape=(timesteps, embedding_dim))
        layer.input = K.variable(np.ones((nb_samples, timesteps, embedding_dim)))
        layer.get_config()
        for train in [True, False]:
            out = K.eval(layer.get_output(train))
            # Make sure the output has the desired shape
            if ret_seq:
<<<<<<< REMOTE
assert(out.shape == (nb_samples, timesteps, output_dim))
=======
assert(out.shape == (nb_samples, output_dim))
=======
assert(out.shape == (nb_samples, timesteps, output_dim))
>>>>>>> LOCAL
            else:
<<<<<<< REMOTE
assert(out.shape == (nb_samples, output_dim))
=======
assert(out1.shape == (nb_samples, output_dim))
=======
assert(out.shape == (nb_samples, output_dim))
>>>>>>> LOCAL
            mask = layer.get_output_mask(train)
    # check statefulness
    model = Sequential()
    model.add(embeddings.Embedding(embedding_num, embedding_dim,
                                   mask_zero=True,
                                   input_length=timesteps,
                                   batch_input_shape=(nb_samples, timesteps)))
    layer = layer_class(output_dim, return_sequences=False,
                        stateful=True,
                        weights=None)
    model.add(layer)
    model.compile(optimizer='sgd', loss='mse')
<<<<<<< REMOTE
out5 = model.predict(np.ones((nb_samples, timesteps)))
=======
out1 = model.predict(np.ones((nb_samples, timesteps)))
=======
out5 = model.predict(np.ones((nb_samples, timesteps)))
>>>>>>> LOCAL
    assert(out1.shape == (nb_samples, output_dim))
    assert(out1.shape == (nb_samples, output_dim))
    # train once so that the states change
    model.train_on_batch(np.ones((nb_samples, timesteps)),
                         np.ones((nb_samples, output_dim)))
<<<<<<< REMOTE
out4 = model.predict(np.ones((nb_samples, timesteps)))
=======
out2 = model.predict(np.ones((nb_samples, timesteps)))
=======
out4 = model.predict(np.ones((nb_samples, timesteps)))
>>>>>>> LOCAL
    # if the state is not reset, output should be different
<<<<<<< REMOTE
assert(out4.max() != out5.max())
=======
assert(out1.max() != out2.max())
=======
assert(out4.max() != out5.max())
>>>>>>> LOCAL
    # check that output changes after states are reset
    # (even though the model itself didn't change)
    layer.reset_states()
    out3 = model.predict(np.ones((nb_samples, timesteps)))
    assert(out2.max() != out3.max())
    # check that container-level reset_states() works
<<<<<<< REMOTE
layer.reset_states()
=======
model.reset_states()
=======
layer.reset_states()
>>>>>>> LOCAL
<<<<<<< REMOTE
out2 = model.predict(np.ones((nb_samples, timesteps)))
=======
out4 = model.predict(np.ones((nb_samples, timesteps)))
=======
out2 = model.predict(np.ones((nb_samples, timesteps)))
>>>>>>> LOCAL
<<<<<<< REMOTE
assert_allclose(out7, out6, atol=1e-5)
=======
assert_allclose(out3, out4, atol=1e-5)
=======
assert_allclose(out7, out6, atol=1e-5)
>>>>>>> LOCAL
    # check that the call to `predict` updated the states
<<<<<<< REMOTE
out1 = model.predict(np.ones((nb_samples, timesteps)))
=======
out5 = model.predict(np.ones((nb_samples, timesteps)))
=======
out1 = model.predict(np.ones((nb_samples, timesteps)))
>>>>>>> LOCAL
<<<<<<< REMOTE
assert(out1.max() != out2.max())
=======
assert(out4.max() != out5.max())
=======
assert(out1.max() != out2.max())
>>>>>>> LOCAL
    # Check masking
<<<<<<< REMOTE
model.reset_states()
=======
layer.reset_states()
=======
model.reset_states()
>>>>>>> LOCAL
<<<<<<< REMOTE
right_padded_input = np.ones((nb_samples, timesteps))
=======
left_padded_input = np.ones((nb_samples, timesteps))
=======
right_padded_input = np.ones((nb_samples, timesteps))
>>>>>>> LOCAL
<<<<<<< REMOTE
right_padded_input[0, -1:] = 0
=======
left_padded_input[0, :1] = 0
=======
right_padded_input[0, -1:] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
right_padded_input[1, -2:] = 0
=======
left_padded_input[1, :2] = 0
=======
right_padded_input[1, -2:] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
right_padded_input[2, -3:] = 0
=======
left_padded_input[2, :3] = 0
=======
right_padded_input[2, -3:] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
out7 = model.predict(right_padded_input)
=======
out6 = model.predict(left_padded_input)
=======
out7 = model.predict(right_padded_input)
>>>>>>> LOCAL
    layer.reset_states()
<<<<<<< REMOTE
left_padded_input = np.ones((nb_samples, timesteps))
=======
right_padded_input = np.ones((nb_samples, timesteps))
=======
left_padded_input = np.ones((nb_samples, timesteps))
>>>>>>> LOCAL
<<<<<<< REMOTE
left_padded_input[0, :1] = 0
=======
right_padded_input[0, -1:] = 0
=======
left_padded_input[0, :1] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
left_padded_input[1, :2] = 0
=======
right_padded_input[1, -2:] = 0
=======
left_padded_input[1, :2] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
left_padded_input[2, :3] = 0
=======
right_padded_input[2, -3:] = 0
=======
left_padded_input[2, :3] = 0
>>>>>>> LOCAL
<<<<<<< REMOTE
out6 = model.predict(left_padded_input)
=======
out7 = model.predict(right_padded_input)
=======
out6 = model.predict(left_padded_input)
>>>>>>> LOCAL
<<<<<<< REMOTE
assert_allclose(out3, out4, atol=1e-5)
=======
assert_allclose(out7, out6, atol=1e-5)
=======
assert_allclose(out3, out4, atol=1e-5)
>>>>>>> LOCAL















def test_SimpleRNN():
    _runner(recurrent.SimpleRNN)


def test_GRU():
<<<<<<< REMOTE
_runner(recurrent.GRU)
=======
_runner(recurrent.LSTM)
=======
_runner(recurrent.GRU)
>>>>>>> LOCAL


def test_LSTM():
<<<<<<< REMOTE
_runner(recurrent.LSTM)
=======
_runner(recurrent.GRU)
=======
_runner(recurrent.LSTM)
>>>>>>> LOCAL


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


def test_batch_input_shape_serialization():
    model = Sequential()
    model.add(embeddings.Embedding(2, 2,
                                   mask_zero=True,
                                   input_length=2,
                                   batch_input_shape=(2, 2)))
    json_data = model.to_json()
    reconstructed_model = model_from_json(json_data)
    assert(reconstructed_model.input_shape == (2, 2))



if __name__ == '__main__':
    pytest.main([__file__])

