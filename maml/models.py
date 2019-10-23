"""
Name: models.py

Usage:
    Stores define models used for MAML.
    Expecting using Tensroflow Keras API only. Keras Function Model or Sequential Model.


Author: Chu-Hung Cheng
"""

import tensorflow as tf
import tensorflow.keras as tk
import model_utils as m_utils
import gin

# MAML is model agnostic, so its better to have a util function that allows user to feed in any type of model
# Ideally, we can have as many model in this function


def build_simple_model(output_shape):
    # Note: Calling this function creates an "unique" model
    ins = tk.Input(shape=(28, 28, 1))

    out = m_utils.conv_block(ins, 64, 3, [1, 1], 'SAME', conv_name="conv1")
    out = m_utils.conv_block(out, 64, 3, [1, 1], 'SAME', conv_name="conv2")
    out = m_utils.conv_block(out, 64, 3, [1, 1], 'SAME', conv_name="conv3")
    out = m_utils.conv_block(out, 64, 3, [1, 1], 'SAME', conv_name="conv4")

    out = tf.math.reduce_mean(out, [1, 2])  # According to Paper
    out = tk.layers.Dense(output_shape, activation='softmax')(out)
    return tk.Model(inputs=ins, outputs=out)  # Keras Functional API


def build_simple_fc_model(output_shape):
    # Note: Calling this function creates an "unique" model
    ins = tk.Input(shape=(28, 28, 1))
    out = tk.layers.Flatten()(ins)
    out = m_utils.fc_block(out, 256)
    out = m_utils.fc_block(out, 128)
    out = m_utils.fc_block(out, 64)
    out = m_utils.fc_block(out, 64)
    out = tk.layers.Dense(output_shape, activation='softmax')(out)
    return tk.Model(inputs=ins, outputs=out)  # Keras Functional API


class SimpleModel(tk.Model):
    def __init__(self, output_shape):
        super().__init__()
        self.conv1 = tk.layers.Conv2D(64, 3, [1, 1], 'SAME',
                                      input_shape=(28, 28, 1))
        self.bn1 = tk.layers.BatchNormalization()
        self.act1 = tk.activations.relu
        self.pool1 = tk.layers.MaxPool2D(pool_size=(2, 2),
                                         padding='valid',
                                         data_format='channels_last')
        self.conv2 = tk.layers.Conv2D(64, 3, [1, 1], 'SAME')
        self.bn2 = tk.layers.BatchNormalization()
        self.act2 = tk.activations.relu
        self.pool2 = tk.layers.MaxPool2D(pool_size=(2, 2),
                                         padding='valid',
                                         data_format='channels_last')

        self.conv3 = tk.layers.Conv2D(64, 3, [1, 1], 'SAME')
        self.bn3 = tk.layers.BatchNormalization()
        self.act3 = tk.activations.relu
        self.pool3 = tk.layers.MaxPool2D(pool_size=(2, 2),
                                         padding='valid',
                                         data_format='channels_last')

        self.conv4 = tk.layers.Conv2D(64, 3, [1, 1], 'SAME')
        self.bn4 = tk.layers.BatchNormalization()
        self.act4 = tk.activations.relu
        self.pool4 = tk.layers.MaxPool2D(pool_size=(2, 2),
                                         padding='valid',
                                         data_format='channels_last')

        self.dense1 = tk.layers.Dense(output_shape, activation='softmax')

    def call(self, x):
        return self.forward(x)

    def forward(self, x):
        x = self.pool1(self.act1(self.bn1(self.conv1(x))))
        x = self.pool2(self.act2(self.bn2(self.conv2(x))))
        x = self.pool3(self.act3(self.bn3(self.conv3(x))))
        x = self.pool4(self.act4(self.bn4(self.conv4(x))))
        x = tf.math.reduce_mean(x, [1, 2])
        x = self.dense1(x)
        return x


class SimpleGanabiModel(tk.Model):
    def __init__(self, output_shape):
        super().__init__()
        self.dense1 = tk.layers.Dense(512, activation=None)
        # self.bn1 = tk.layers.BatchNormalization()
        self.act1 = tk.activations.relu

        self.dense2 = tk.layers.Dense(256, activation=None)
        # self.bn2 = tk.layers.BatchNormalization()
        self.act2 = tk.activations.relu

        self.dense3 = tk.layers.Dense(128, activation=None)
        # self.bn3 = tk.layers.BatchNormalization()
        self.act3 = tk.activations.relu

        self.dense4 = tk.layers.Dense(64, activation=None)
        # self.bn4 = tk.layers.BatchNormalization()
        self.act4 = tk.activations.relu

        self.dense5 = tk.layers.Dense(32, activation=None)
        # self.bn5 = tk.layers.BatchNormalization()
        self.act5 = tk.activations.relu

        self.out = tk.layers.Dense(output_shape, activation='softmax')

    def call(self, x):
        return self.forward(x)

    def forward(self, x):
        # x = self.act1(self.bn1(self.dense1(x)))
        # x = self.act2(self.bn2(self.dense2(x)))
        # x = self.act3(self.bn3(self.dense3(x)))
        # x = self.act4(self.bn4(self.dense4(x)))
        # x = self.act5(self.bn5(self.dense5(x)))

        x = self.act1(self.dense1(x))
        x = self.act2(self.dense2(x))
        x = self.act3(self.dense3(x))
        x = self.act4(self.dense4(x))
        x = self.act5(self.dense5(x))

        x = self.out(x)

        return x


@gin.configurable
class NewGanabiModel(tk.Model):
    def __init__(self,
                 model_name,
                 hidden_sizes,
                 output_shape,
                 act_fn,
                 bNorm,
                 dropout_rate):

        super().__init__()

        self.model_name = model_name
        self.bNorm = bNorm
        self.dropout_rate = dropout_rate

        model_layers = []
        for i, h_size in enumerate(hidden_sizes):
            # Dense
            layer = tk.layers.Dense(h_size,
                                    activation=None,
                                    name="{}-dense-{}".format(self.model_name, i))
            model_layers.append(layer)

            # BNorm
            if self.bNorm:
                bn_layer = tk.layers.BatchNormalization(
                    name="{}-bn-{}".format(self.model_name, i))
                model_layers.append(bn_layer)

            # Activation
            act_layer = self.get_act_fn(act_fn, i)
            model_layers.append(act_layer)

            # Dropout
            if self.dropout_rate > 0.0:
                dropout_layer = tk.layers.Dropout(
                    rate=self.dropout_rate,
                    name="{}-dropout-{}".format(self.model_name, i))
                model_layers.append(dropout_layer)

        self.model_layers = model_layers
        self.out = tk.layers.Dense(output_shape, activation='softmax')

    def get_act_fn(self, act, i):
        if act == 'relu':
            return tk.layers.ReLU(name="{}-act-{}".format(self.model_name, i))
        elif act == 'prelu':
            return tk.layers.PReLU(name="{}-act-{}".format(self.model_name, i))
        elif act == 'lrelu':
            return tk.layers.LeakyReLU(name="{}-act-{}".format(self.model_name, i))
        elif act == 'tanh':
            return tk.activations.tanh
        elif act == 'sigmoid':
            return tk.activations.sigmoid
        else:
            raise("Unknown Activation Function type {}".format(act))

    def call(self, x):
        return self.forward(x)

    def forward(self, x):
        for i in range(len(self.model_layers)):
            x = self.model_layers[i](x)

        x = self.out(x)

        return x
