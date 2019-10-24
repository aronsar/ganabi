import multiprocessing as mp
import pickle
import random
import re
from itertools import repeat
from pprint import pprint
import time
import os
import numpy as np
import tensorflow as tf
import sys

sys.path.append('..')            # nopep8
sys.path.append('../../utils/')  # nopep8

from utils import binary_list_to_int  # nopep8
import DataGenerator as dg           # nopep8

# mp.set_start_method('spawn', True)  # Allow Debugging MultiProcess in VSCode


def sample_task_batch(labels, config):
    """
    A Multi-Processing Function that returns a batch of an agent's data
    """
    # start = time.time()
    # Sanity Check
    if len(labels) != 1:
        raise("Incorrect Agent Label Number. Should Only sample one agent per task")

    agent_label = labels[0]
    is_train = config[0]

    res = dg.DataGenerator.dataset_obj.retrieve_agent_batch(
        agent_label, is_train)

    # end = time.time()
    # print("Time Spent for batching a task {}".format(end - start))
    # print("Start at {} Ends at {}".format(start, end))

    # Set train batch
    return res


def read_pkl(pkl_path, config):
    """
    A Multi-Processing Function that reads an agent's pickle file and instantiate a generator
    """
    obs_dim, act_dim, batch_size, num_support, num_query, shuffle = config
    name = re.split('/', pkl_path)[-1]
    pkl_files = os.listdir(pkl_path)
    # TODO: Handle Multiple Pickle Files in a given directory
    for pkl_file in pkl_files:
        with open(os.path.join(pkl_path, pkl_file), 'rb') as f:
            f.seek(0)
            data = pickle.load(f)
            f.close()

    data = np.array(data)
    return AgentGenerator(X=data[:, 0],
                          Y=data[:, 1],
                          name=name,
                          obs_dim=obs_dim,
                          act_dim=act_dim,
                          batch_size=batch_size,
                          num_support=num_support,
                          num_query=num_query,
                          shuffle=shuffle)


class AgentGenerator(tf.keras.utils.Sequence):
    """Generate data from preset directory containing pickle files"""

    def __init__(self, X, Y, name, obs_dim=658, act_dim=20, batch_size=32, num_support=10,
                 num_query=1, shuffle=True):
        """
        Arguments:
.
        """
        self.name = name
        self.obs_dim = obs_dim
        self.act_dim = act_dim

        print("########################## Init Agent {}'s Generator ##########################".format(self.name))

        assert(X.shape[0] == Y.shape[0])
        self.X = self.transform_x(X)
        self.Y = self.transform_y(Y)
        assert(self.X.shape[0] == self.Y.shape[0])

        self.num_support = num_support
        self.num_query = num_query
        self.shot_size = batch_size
        self.batch_size = batch_size * (self.num_support + self.num_query)

        self.shuffle = shuffle
        self.indices = None  # keep track of indices during training
        self.index = 0
        self.on_epoch_end()

    def transform_x(self, data):
        """ Convert the obs into a 1-D vector"""
        res = []
        for i in range(data.shape[0]):
            res.append(np.array(data[i]))

        # Way Too costly
        # res = np.expand_dims(np.concatenate(res), axis=1)
        # res = np.apply_along_axis(
        #         lambda x: binary_list_to_int.revert(x[0], self.obs_dim), 1, res)
        return np.concatenate(res)

    def transform_y(self, data):
        """ Convert the y into a 1-D sparse vector"""
        res = []
        for i in range(data.shape[0]):
            res.append(np.argmax(np.array(data[i]), axis=1))

        return np.concatenate(res)

    def __len__(self):
        """Denotes the number of batches per epoch"""
        return int(np.floor(self.X.shape[0] / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data"""
        # get the subset; index = 0, 1, 2, ...
        start, end = index * self.batch_size, (index+1) * self.batch_size
        indices = self.indices[start:end]
        # Take the subsets
        X = self.X[indices]
        Y = self.Y[indices]

        X = np.vstack([binary_list_to_int.revert(X[i], self.obs_dim)
                       for i in range(X.shape[0])])

        return X, Y

    def get_next_batch(self):
        """
        Retrieve a batch of x_support, y_support, x_query, y_query
        """
        x, y = self.__getitem__(self.index)
        self.index += 1
        self.check_epoch_end()

        x_support = x[:self.shot_size*self.num_support]
        y_support = y[:self.shot_size*self.num_support]
        x_query = x[self.shot_size*self.num_support:]
        y_query = y[self.shot_size*self.num_support:]

        x_support = x_support.reshape(
            self.num_support, self.shot_size, self.obs_dim)
        y_support = y_support.reshape(self.num_support, self.shot_size)
        x_query = x_query.reshape(self.num_query, self.shot_size, self.obs_dim)
        y_query = y_query.reshape(self.num_query, self.shot_size)

        # x_support = x_support.reshape(
        #     self.num_support, self.shot_size, 1)
        # y_support = y_support.reshape(self.num_support, self.shot_size)
        # x_query = x_query.reshape(self.num_query, self.shot_size, 1)
        # y_query = y_query.reshape(self.num_query, self.shot_size)

        return (x_support, y_support, x_query, y_query)

    def check_epoch_end(self):
        """Calls on_epoch_end if reaches end of an epoch"""
        if self.index >= self.__len__():
            self.on_epoch_end()

    def on_epoch_end(self):
        """Updates indices after each epoch"""
        self.index = 0
        self.indices = np.arange(self.X.shape[0])
        if self.shuffle == True:
            np.random.shuffle(self.indices)


class Dataset(object):
    def __init__(self, config_obj, data_dir):
        self.obs_dim = config_obj.get("obs_dim")
        self.act_dim = config_obj.get("act_dim")
        self.batch_size = config_obj.get("batch_size")
        self.train_support = config_obj.get("train_support")
        self.train_query = config_obj.get("train_query")
        self.test_support = config_obj.get("test_support")
        self.test_query = config_obj.get("test_query")
        self.shuffle = config_obj.get("shuffle")

        self.agent_path = os.path.join(data_dir, 'ganabi/train')
        # Define multi-process function name, can be reused
        self.mp_func = read_pkl

        self.test_agent_name = config_obj.get("test_agent")
        self.train_agent_name = os.listdir(self.agent_path)
        self.train_agent_name.remove(self.test_agent_name)
        self.test_agent_name = [self.test_agent_name]

        self.train_labels_len = len(self.train_agent_name)
        self.test_labels_len = len(self.test_agent_name)

        self.train_generators = self._read_agent_data(
            self.train_agent_name, True)
        self.test_generators = self._read_agent_data(
            self.test_agent_name, False)

    def _read_agent_data(self, agent_name, train, process_count=8):
        """
        Multi-Process Wrapper function that reads the piclke data files and initialize agent data generator
        """
        # Define multi-process function arguments
        agent_paths = [os.path.join(self.agent_path, name)
                       for name in agent_name]

        # Argument wrapper
        mp_args = zip(agent_paths,
                      repeat((self.obs_dim,
                              self.act_dim,
                              self.batch_size,
                              self.train_support if train else self.test_support,
                              self.train_query if train else self.test_query,
                              self.shuffle)))

        with mp.Pool(process_count) as p:
            return p.starmap(self.mp_func, mp_args)

    def retrieve_agent_batch(self, agent_name, train=True):
        if train:
            return self.train_generators[agent_name].get_next_batch()
        else:
            return self.test_generators[agent_name].get_next_batch()
