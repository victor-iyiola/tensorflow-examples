"""A Guide to TF Layers: Building a Convolutional Neural Network.

   @author
     Victor I. Afolabi
     Artificial Intelligence & Software Engineer.
     Email: javafolabi@gmail.com
     GitHub: https://github.com/victor-iyiola

   @project
     File: mnist.py
     Created on 18 May, 2018 @ 5:26 PM.

   @license
     MIT License
     Copyright (c) 2018. Victor I. Afolabi. All rights reserved.
"""

from __future__ import print_function, absolute_import, division

import argparse

import numpy as np
import tensorflow as tf

# TensorFlow log level.
tf.logging.set_verbosity(tf.logging.INFO)

# Clear the default graph.
tf.reset_default_graph()

# Command line arguments.
args = argparse.Namespace


def make_one_hot(indices: np.ndarray, depth: int, dtype: np.dtype = np.int32):
    """Returns a one-hot array.

    Args:
        indices (np.ndarray): Array to be converted.
        depth (int): How many elements per item.
        dtype (np.dtype): Encoded array data type.

    Examples:
        ```python
        >>> y = np.random.randint(low=0, high=10, size=(5,))
        >>> print(y)
        [4 9 6 7 5]
        >>> y_hot = make_one_hot(indices=y, depth=10)
        >>> print(y_hot)
        [[0 0 0 0 1 0 0 0 0 0]
         [0 0 0 0 0 0 0 0 0 1]
         [0 0 0 0 0 0 1 0 0 0]
         [0 0 0 0 0 0 0 1 0 0]
         [0 0 0 0 0 1 0 0 0 0]]
        ```

    Returns:
        one_hot (np.ndarray): One-hot encoded array.
    """
    hot = np.zeros(shape=(indices.shape[0], depth), dtype=dtype)
    for i, index in enumerate(indices):
        hot[i, index] = 1.
    return hot


def load_data(one_hot: bool = False):
    """Load MNIST dataset.

    Args:
        one_hot (bool):
            Maybe convert labels to one-hot arrays.

    Examples:
        ```python
        >>> train, test = load_data(one_hot=True)
        >>> X_train, y_train = train
        >>> X_test, y_test = test
        >>> print('Train: images = {}\t labels = {}'.format(X_train.shape, y_train.shape))
        Train: images = (60000, 28, 28)	 labels = (60000, 10)

        >>> print('Test: images = {}\t labels = {}'.format(X_test.shape, y_test.shape))
        Test: images = (10000, 28, 28)	 labels = (10000, 10)

        ```

    Returns:
        tuple: train, test
    """
    # Maybe download mnist dataset.
    train, test = tf.keras.datasets.mnist.load_data()

    # Split into images & labels.
    X_train, y_train = train
    X_test, y_test = test

    # Release train & test from memory.
    del train, test

    # Convert images to np.float32
    X_train = np.array(X_train, dtype=np.float32)
    X_test = np.array(X_test, dtype=np.float32)

    # Convert labels to one hot vectors.
    if one_hot:
        y_train = make_one_hot(indices=y_train, depth=10)
        y_test = make_one_hot(indices=y_test, depth=10)

    return (X_train, y_train), (X_test, y_test)


def make_dataset(features: np.ndarray, labels: np.ndarray = None):
    """Create dataset object from features &/or labels.

    Args:
        features (np.ndarray): Feature column.
        labels (np.ndarray): Dataset labels.

    Returns:
        tf.data.Dataset: Pre-processed dataset object.
    """
    # Give feature column a corresponding label.
    features = {args.feature_col: features}

    # Create dataset from features &/or labels.
    if labels is not None:
        dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    else:
        dataset = tf.data.Dataset.from_tensor_slices(features)

    # Dataset transformation.
    dataset = dataset.batch(batch_size=args.batch_size)
    dataset = dataset.shuffle(buffer_size=args.shuffle_rate)
    dataset = dataset.repeat(count=args.data_transform_count)

    # Return pre-processed dataset object.
    return dataset


def input_fn(features: np.ndarray, labels: np.ndarray = None,
             epochs: int = 1, shuffle: bool = False):
    """Creates input function given features & (maybe) labels.

    Args:
        features (np.ndarray): Input images.
        labels (np.ndarray): Data targets.
        epochs (int): Number of passes through data.
        shuffle (bool): Maybe shuffle dataset.

    Returns:
        Function, that has signature of ()->(dict of `features`, `targets`)
    """
    # Using raw numpy input function. (We only have pandas & numpy).
    return tf.estimator.inputs.numpy_input_fn(
        x={args.feature_col: features},
        y=labels,
        num_epochs=epochs,
        shuffle=shuffle
    )


def model_fn(features: tf.Tensor, labels: tf.Tensor, mode: tf.estimator.ModeKeys):
    """Construct a 2-layer convolutional network.

    Arguments:
        features (tf.Tensor):
            Dataset images with shape (batch_size, img_flat) or
            (batch_size, img_width, img_height, img_depth).

        labels (tf.Tensor):
            Dataset labels (one-hot encoded).

        mode (tf.estimator.ModeKeys):
            One of tf.estimator.ModeKeys.PREDICT, tf.estimator.ModeKeys.TRAIN,
            or tf.estimator.ModeKeys.EVAL.

    Returns:
        tf.estimator.EstimatorSpec:
            Ops and objects returned from `model_fn` and passed to
            tf.estimator.Estimator.
    """
    # Constructing a Convolutional Model.
    with tf.name_scope("cnn_model"):
        # Model Architecture/layers.
        with tf.name_scope("layers"):
            with tf.name_scope("input"):
                # Input layer.
                input_layer = tf.reshape(tensor=features[args.feature_col],
                                         shape=[-1, args.img_size,
                                                args.img_size, args.img_depth],
                                         name="reshape")

            # Convolutional block #1.
            with tf.name_scope("conv1"):
                # Convolutional layer #1.
                conv1 = tf.layers.conv2d(inputs=input_layer,
                                         filters=args.filter_conv1,
                                         kernel_size=args.kernel_size,
                                         padding="same",
                                         activation=tf.nn.relu)

                # Pooling layer #1.
                pool1 = tf.layers.max_pooling2d(inputs=conv1,
                                                pool_size=args.pool_size,
                                                strides=2, name="my_pool")

            # Convolutional block #2.
            with tf.name_scope("conv2"):
                # Convolutional layer #2.
                conv2 = tf.layers.conv2d(inputs=pool1,
                                         filters=args.filter_conv2,
                                         kernel_size=args.kernel_size,
                                         activation=tf.nn.relu)

                # Pooling layer #2.
                pool2 = tf.layers.max_pooling2d(inputs=conv2,
                                                pool_size=args.pool_size,
                                                strides=2, name="my_pool")

            # Fully connected layer.
            with tf.name_scope("fully_connected"):
                # Flatten layer (Prep for fully connected layers).
                flatten = tf.layers.flatten(inputs=pool2, name="flatten")

                # Fully connected layer activation.
                dense = tf.layers.dense(inputs=flatten, units=args.dense_units,
                                        activation=tf.nn.relu,
                                        name="dense")

                # Dropout for regularization.
                dropout = tf.layers.dropout(inputs=dense, rate=args.dropout,
                                            training=mode == tf.estimator.ModeKeys.TRAIN,
                                            name="dropout")

            # Output layer.
            with tf.name_scope("output"):
                logits = tf.layers.dense(inputs=dropout, units=args.num_classes,
                                         name="logits")

        # Predictions (classes & probabilities).
        with tf.name_scope("predictions"):
            predictions = {
                "classes": tf.argmax(input=logits, axis=1, name="classes"),
                "probabilities": tf.nn.softmax(logits=logits, name="probabilities")
            }

        # If mode=tf.estimator.ModeKeys.PREDICT, return the predictions.
        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

        # Calculate loss (for both TRAIN & EVAL modes).
        loss = tf.losses.softmax_cross_entropy(onehot_labels=labels,
                                               logits=logits,
                                               reduction=tf.losses.Reduction.MEAN)

        # Configure the training op (for TRAIN mode).
        if mode == tf.estimator.ModeKeys.TRAIN:
            with tf.name_scope("train"):
                optimizer = tf.train.RMSPropOptimizer(learning_rate=args.learning_rate,
                                                      decay=args.decay_rate)
                train_op = optimizer.minimize(loss=loss,
                                              global_step=tf.train.get_or_create_global_step(),
                                              name="train_op")
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

        # Add Evaluation metrics (for EVAL mode).
        if mode == tf.estimator.ModeKeys.EVAL:
            with tf.name_scope("evaluation"):
                # Evaluation metrics.
                eval_metrics_op = {
                    "accuracy": tf.metrics.accuracy(labels=labels,
                                                    predictions=predictions["probabilities"],
                                                    name="accuracy")
                }
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss,
                                              eval_metric_ops=eval_metrics_op)


def main():
    # Load MNIST dataset.
    train, test = load_data(one_hot=True)

    # Split into image & labels.
    X_train, y_train = train
    X_test, y_test = test

    # Create Estimator.
    clf = tf.estimator.Estimator(model_fn=model_fn, model_dir=args.logdir)

    # Logging hook to track training progress. Tensors to log.
    log_tensors = {
        # Probability tensor name (in the default graph).
        "probabilities": "cnn_model/predictions/probabilities:0",
    }
    logging_hook = tf.train.LoggingTensorHook(tensors=log_tensors,
                                              every_n_iter=args.log_every,
                                              at_end=False)

    # Train the model.
    train_input_fn = input_fn(features=X_train, labels=y_train,
                              epochs=args.epochs, shuffle=True)
    clf.train(input_fn=train_input_fn, hooks=[logging_hook],
              max_steps=args.steps)

    # Evaluate the model.
    eval_input_fn = input_fn(features=X_test, labels=y_test,
                             epochs=1, shuffle=False)
    results = clf.evaluate(input_fn=eval_input_fn)

    print('Global steps = {:,}\tAccuracy = {:.02%}\tLoss = {:.4f}'
          .format(results['global_step'], results['accuracy'], results['loss']))


if __name__ == '__main__':
    # Command line argument parser.
    parser = argparse.ArgumentParser()

    # Input arguments.
    parser.add_argument('--img_size', type=int, default=28,
                        help="Image size. The default for MNIST data is 28")
    parser.add_argument('--img_depth', type=int, default=1,
                        help="Image channel. The default for MNIST data is 1, "
                             "which signifies image is a Monochrome image.")
    parser.add_argument('--num_classes', type=int, default=10,
                        help="Number of classes to be predicted.")

    # Dataset arguments.
    parser.add_argument('--batch_size', type=int, default=128,
                        help="Mini batch size. Use lower batch size if running on CPU.")
    parser.add_argument('--shuffle_rate', type=int, default=1000,
                        help="Dataset shuffle rate.")
    parser.add_argument('--data_transform_count', type=int, default=5,
                        help="Dataset transform repeat count. "
                             "Use smaller (or 1) if running on CPU")
    parser.add_argument('--feature_col', type=str, default="images",
                        help="Feature column label for tf.feature_column")

    # Estimator arguments.
    parser.add_argument('--save_dir', type=str, default="../../saved/tutorials/mnist",
                        help="Specifies the directory where model data "
                             "(checkpoints) will be saved.")
    parser.add_argument('--logdir', type=str, default="../../saved/tutorials/mnist",
                        help="Specifies the directory where model data "
                             "(checkpoints) will be saved.")
    parser.add_argument('--log_every', type=int, default=50,
                        help="Log specified tensors every ``log_every`` iterations.")

    # Network arguments.
    parser.add_argument('--kernel_size', type=int, default=5,
                        help="Kernel size for each convolution. "
                             "default [5, 5]")
    parser.add_argument('--pool_size', type=int, default=2,
                        help="Down-sampling filter size. default [2, 2]")
    parser.add_argument('--filter_conv1', type=int, default=32,
                        help="Size of 1st convolutional filters.")
    parser.add_argument('--filter_conv2', type=int, default=64,
                        help="Size of 2nd convolutional filters.")
    parser.add_argument('--dense_units', type=int, default=1024,
                        help="Number of neurons in the fully connected layer.")
    parser.add_argument('--dropout', type=float, default=0.4,
                        help="Dropout regularization rate (probability that a given "
                             "element will be dropped during training).")

    # Training & optimizer arguments.
    parser.add_argument('--epochs', type=int, default=None,
                        help="Number of training epochs. Signifies the number of "
                             "times to loop through a complete training iteration. "
                             "Default is `None` meaning that the  model will train "
                             "until the specified number of steps is reached.")
    parser.add_argument('--steps', type=int, default=1000,
                        help="Number of training steps. Represents the number of "
                             "times to loop through a complete mini-batch cycle.")
    parser.add_argument('--learning_rate', type=float, default=1e-3,
                        help="Learning rate for RMSPropOptimizer.")
    parser.add_argument('--decay_rate', type=float, default=0.99,
                        help="Decay rate for RMSPropOptimizer.")

    # Parse command line arguments.
    args = parser.parse_args()
    print(args)

    # Start program execution.
    main()
