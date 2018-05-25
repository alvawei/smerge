import numpy as np

from keras import backend as K
from keras.layers.core import *
from keras.layers.convolutional import *
from keras.layers.recurrent import SimpleRNN


def check_layer_output_shape(layer, input_data):
    ndim = len(input_data.shape)
    layer.input = K.placeholder(ndim=ndim)
    layer.set_input_shape(input_data.shape)
    expected_output_shape = layer.output_shape[1:]
    function = K.function([layer.input], [layer.get_output()])
    output = function([input_data])[0]
    assert output.shape[1:] == expected_output_shape























if __name__ == "__main__":
    pytest.main([__file__])

