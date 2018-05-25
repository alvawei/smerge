"""Interface converters for Keras 1 support in Keras 2.
"""
import six
import warnings





def raise_duplicate_arg_error(old_arg, new_arg):
    raise TypeError('For the `' + new_arg + '` argument, '
                    'the layer received both '
                    'the legacy keyword argument '
                    '`' + old_arg + '` and the Keras 2 keyword argument '
                    '`' + new_arg + '`. Stick with the latter!')

legacy_dense_support = generate_legacy_interface(
    allowed_positional_args=['units'],
    conversions=[('output_dim', 'units'),
                 ('init', 'kernel_initializer'),
                 ('W_regularizer', 'kernel_regularizer'),
                 ('b_regularizer', 'bias_regularizer'),
                 ('W_constraint', 'kernel_constraint'),
                 ('b_constraint', 'bias_constraint'),
                 ('bias', 'use_bias')])

legacy_dropout_support = generate_legacy_interface(
    allowed_positional_args=['rate', 'noise_shape', 'seed'],
    conversions=[('p', 'rate')])

legacy_pooling1d_support = generate_legacy_interface(
    allowed_positional_args=['pool_size', 'strides', 'padding'],
    conversions=[('pool_length', 'pool_size'),
                 ('stride', 'strides'),
                 ('border_mode', 'padding')])

legacy_prelu_support = generate_legacy_interface(
    allowed_positional_args=['alpha_initializer'],
    conversions=[('init', 'alpha_initializer')])

legacy_gaussiannoise_support = generate_legacy_interface(
    allowed_positional_args=['stddev'],
    conversions=[('sigma', 'stddev')])

