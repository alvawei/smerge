# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""ResNet model for classifying images from CIFAR-10 dataset.

Support single-host training with one or multiple devices.

ResNet as proposed in:
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
Deep Residual Learning for Image Recognition. arXiv:1512.03385

CIFAR-10 as in:
http://www.cs.toronto.edu/~kriz/cifar.html


"""
from __future__ import division
from __future__ import print_function

import argparse
import functools
import itertools
import os
import six

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import cifar10
import cifar10_model
import cifar10_utils


tf.logging.set_verbosity(tf.logging.INFO)


<<<<<<< REMOTE
def get_model_fn(num_gpus, variable_strategy, num_workers, sync):
=======
def get_model_fn(num_gpus, variable_strategy, num_workers):
=======
def get_model_fn(num_gpus, variable_strategy, data_format, num_workers):
>>>>>>> LOCAL
  """Returns a function that will build the resnet model."""
  def _resnet_model_fn(features, labels, mode, params):
    """Resnet model body.

    Support single host, one or more GPU training. Parameter distribution can
    be either one of the following scheme.
    1. CPU is the parameter server and manages gradient updates.
    2. Parameters are distributed evenly across all GPUs, and the first GPU
       manages gradient updates.

    Args:
      features: a list of tensors, one for each tower
      labels: a list of tensors, one for each tower
      mode: ModeKeys.TRAIN or EVAL
      params: Hyperparameters suitable for tuning
    Returns:
      A EstimatorSpec object.
    """
    is_training = (mode == tf.estimator.ModeKeys.TRAIN)
    weight_decay = params.weight_decay
    momentum = params.momentum
    tower_features = features
    tower_labels = labels
    tower_losses = []
    tower_gradvars = []
    tower_preds = []
    if num_gpus == 0:
      num_devices = 1
      device_type = 'cpu'
    else:
      num_devices = num_gpus
      device_type = 'gpu'
    for i in range(num_devices):
      worker_device = '/{}:{}'.format(device_type, i)
      if variable_strategy == 'CPU':
          device_setter = cifar10_utils.local_device_setter(
              worker_device=worker_device)
      elif variable_strategy == 'GPU':
          device_setter = cifar10_utils.local_device_setter(
              ps_device_type='gpu',
              worker_device=worker_device,
              ps_strategy=tf.contrib.training.GreedyLoadBalancingStrategy(
                num_gpus, tf.contrib.training.byte_size_load_fn))
      with tf.variable_scope('resnet', reuse=bool(i != 0)):
        with tf.name_scope('tower_%d' % i) as name_scope:
          with tf.device(device_setter):
            loss, gradvars, preds = _tower_fn(
                is_training, weight_decay, tower_features[i], tower_labels[i],
                data_format, params['num_layers'], params['batch_norm_decay'],
                params.batch_norm_epsilon)
            tower_losses.append(loss)
            tower_gradvars.append(gradvars)
            tower_preds.append(preds)
            if i == 0:
              # Only trigger batch_norm moving mean and variance update from
              # the 1st tower. Ideally, we should grab the updates from all
              # towers but these stats accumulate extremely fast so we can
              # ignore the other stats from the other towers without
              # significant detriment.
              update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS,
                                             name_scope)
    # Now compute global loss and gradients.
    gradvars = []
    with tf.name_scope('gradient_averaging'):
      all_grads = {}
      for grad, var in itertools.chain(*tower_gradvars):
        if grad is not None:
          all_grads.setdefault(var, []).append(grad)
      for var, grads in six.iteritems(all_grads):
        # Average gradients on the same device as the variables
        # to which they apply.
        with tf.device(var.device):
          if len(grads) == 1:
            avg_grad = grads[0]
          else:
            avg_grad = tf.multiply(tf.add_n(grads), 1. / len(grads))
        gradvars.append((avg_grad, var))
    # Device that runs the ops to apply global gradient updates.
    consolidation_device = '/gpu:0' if variable_strategy == 'GPU' else '/cpu:0'
    with tf.device(consolidation_device):
      # Suggested learning rate scheduling from
      # https://github.com/ppwwyyxx/tensorpack/blob/master/examples/ResNet/cifar10-resnet.py#L155
      num_batches_per_epoch = cifar10.Cifar10DataSet.num_examples_per_epoch(
          'train') // (params.train_batch_size * num_workers)
      boundaries = [
          num_batches_per_epoch * x
          for x in np.array([82, 123, 300], dtype=np.int64)
      ]
      staged_lr = [params.learning_rate * x for x in [1, 0.1, 0.01, 0.002]]
      learning_rate = tf.train.piecewise_constant(tf.train.get_global_step(),
                                                  boundaries, staged_lr)
      # Create a nicely-named tensor for logging
      learning_rate = tf.identity(learning_rate, name='learning_rate')
      optimizer = tf.train.MomentumOptimizer(
          learning_rate=learning_rate, momentum=momentum)
      if sync:
        optimizer = tf.train.SyncReplicasOptimizer(
        sync_replicas_hook = optimizer.make_session_run_hook(True)
        chief_hooks.append(sync_replicas_hook)
      chief_hooks = []
      # Create single grouped train op
      train_op = [
          optimizer.apply_gradients(
              gradvars, global_step=tf.train.get_global_step())
      ]
      train_op.extend(update_ops)
      train_op = tf.group(*train_op)
      predictions = {
          'classes':
              tf.concat([p['classes'] for p in tower_preds], axis=0),
          'probabilities':
              tf.concat([p['probabilities'] for p in tower_preds], axis=0)
      }
      stacked_labels = tf.concat(labels, axis=0)
      metrics = {
              tf.metrics.accuracy(stacked_labels, predictions['classes'])
      }
      loss = tf.reduce_mean(tower_losses, name='loss')
    return tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=predictions,
        loss=loss,
        train_op=train_op,
        training_chief_hooks=chief_hooks,
        eval_metric_ops=metrics)
  return _resnet_model_fn























# create experiment














if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--data-dir',
      type=str,
      required=True,
      help='The directory where the CIFAR-10 input data is stored.')
  parser.add_argument(
      '--job-dir',
      type=str,
      required=True,
      help='The directory where the model will be stored.')
  parser.add_argument(
      '--variable-strategy',
      choices=['CPU', 'GPU'],
      type=str,
      default='CPU',
      help='Where to locate variable operations')
  parser.add_argument(
      '--num-gpus',
      type=int,
      default=1,
      help='The number of gpus used. Uses only CPU if set to 0.')
  parser.add_argument(
      '--num-layers',
      type=int,
      default=44,
      help='The number of layers of the model.')
  parser.add_argument(
      '--train-steps',
      type=int,
      default=80000,
      help='The number of steps to use for training.')
  parser.add_argument(
      '--train-batch-size',
      type=int,
      default=128,
      help='Batch size for training.')
  parser.add_argument(
      '--eval-batch-size',
      type=int,
      default=100,
      help='Batch size for validation.')
  parser.add_argument(
      '--momentum',
      type=float,
      default=0.9,
      help='Momentum for MomentumOptimizer.')
  parser.add_argument(
      '--weight-decay',
      type=float,
      default=2e-4,
      help='Weight decay for convolutions.')
  parser.add_argument(
      '--learning-rate',
      type=float,
      default=0.1,
      help="""\
      This is the inital learning rate value. The learning rate will decrease
      during training. For more details check the model_fn implementation in
      this file.\
      """)
  parser.add_argument(
      '--use-distortion-for-training',
      type=bool,
      default=True,
      help='If doing image distortion for training.')
  parser.add_argument(
      '--sync',
      action='store_true',
      default=False,
      '--data-format',
      type=str,
      default=None,
      help="""\
      If not set, the data format best for the training device is used. 
      Allowed values: channels_first (NCHW) channels_last (NHWC).\
      """)
      help="""\
      If present when running in a distributed environment will run on sync mode.\
      """)
      help="""\
      Number of threads to use for intra-op parallelism. When training on CPU
      set to 0 to have the system pick the appropriate number or alternatively
      set it to the number of physical CPU cores.\
      """
  parser.add_argument(
      '--num-intra-threads',
      type=int,
      default=0,
  parser.add_argument(
  parser.add_argument(
      '--num-inter-threads',
      type=int,
      default=0,
      help="""\
      Number of threads to use for inter-op parallelism. If set to 0, the
      system will pick an appropriate number.\
      """)
  parser.add_argument(
      '--log-device-placement',
      action='store_true',
      default=False,
      help='Whether to log device placement.')
  parser.add_argument(
      '--batch-norm-decay',
      type=float,
      default=0.997,
      help='Decay for batch norm.')
  parser.add_argument(
      '--batch-norm-epsilon',
      type=float,
      default=1e-5,
      help='Epsilon for batch norm.')
  args = parser.parse_args()
  if args.num_gpus < 0:
        'Invalid GPU count: \"--num-gpus\" must be 0 or a positive integer.')
  if args.num_gpus == 0 and args.variable_strategy == 'GPU':
    raise ValueError(
        'num-gpus=0, CPU must be used as parameter server. Set'
        '--variable-strategy=CPU.')
    raise ValueError(
  if (args.num_layers - 2) % 6 != 0:
    raise ValueError('Invalid --num-layers parameter.')
  if args.num_gpus != 0 and args.train_batch_size % args.num_gpus != 0:
    raise ValueError('--train-batch-size must be multiple of --num-gpus.')
  if args.num_gpus != 0 and args.eval_batch_size % args.num_gpus != 0:
    raise ValueError('--eval-batch-size must be multiple of --num-gpus.')
  main(**vars(args))



