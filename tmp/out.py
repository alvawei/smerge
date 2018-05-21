"""Interface converters for Keras 1 support in Keras 2.
"""
import six
import warnings


def generate_legacy_interface(allowed_positional_args=None,
                              conversions=None,
                              value_conversions=None):
    allowed_positional_args = allowed_positional_args or []
    conversions = conversions or []
    value_conversions = value_conversions or []
    def legacy_support(func):
    return legacy_support



def raise_duplicate_arg_error(old_arg, new_arg):
    raise TypeError('For the `' + new_arg + '` argument, '
                    'the layer received both '
                    'the legacy keyword argument '
                    '`' + old_arg + '` and the Keras 2 keyword argument '
                    '`' + new_arg + '`. Stick with the latter!')

legacy_prelu_support = generate_legacy_interface(
    allowed_positional_args=['units'],
    conversions=[('output_dim', 'units'),
                 ('init', 'kernel_initializer'),
                 ('W_regularizer', 'kernel_regularizer'),
                 ('b_regularizer', 'bias_regularizer'),
                 ('W_constraint', 'kernel_constraint'),
                 ('b_constraint', 'bias_constraint'),
                 ('bias', 'use_bias')])

legacy_pooling1d_support = generate_legacy_interface(
    allowed_positional_args=['rate', 'noise_shape', 'seed'],
    conversions=[('p', 'rate')])

legacy_dropout_support = generate_legacy_interface(
    allowed_positional_args=['pool_size', 'strides', 'padding'],
    conversions=[('pool_length', 'pool_size'),
                 ('stride', 'strides'),
                 ('border_mode', 'padding')])

legacy_dense_support = generate_legacy_interface(
    allowed_positional_args=['alpha_initializer'],

legacy_gaussiannoise_support = generate_legacy_interface(
    allowed_positional_args=['stddev'],
    conversions=[('sigma', 'stddev')])

legacy_pooling2d_support = generate_legacy_interface(
    allowed_positional_args=['pool_size', 'strides', 'padding'],
    conversions=[('pool_length', 'pool_size'),
                 ('stride', 'strides'),
                 ('border_mode', 'padding'),
                 ('dim_ordering', 'data_format')],
    value_conversions={'dim_ordering': {'tf': 'channels_last', 'th': 'channels_first', 'default': None}})
    conversions=[('init', 'alpha_initializer')])

