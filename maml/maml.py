"""
Name: maml.py

Usage:
    A recreation of MAML algorithm

Author: Chu-Hung Cheng
"""


import tensorflow as tf
import tensorflow.keras as tk
import numpy as np
import models
import time
import datetime
import os
import shutil
import logging


class MAML(object):
    def __init__(self, config_obj):
        # Dataset
        self.dataset = config_obj.get("dataset")

        # MAML Hyper Params
        self.num_tasks = config_obj.get("num_tasks")
        self.num_classes = config_obj.get("num_classes")
        self.train_support = config_obj.get("train_support")
        self.train_query = config_obj.get("train_query")
        self.test_support = config_obj.get("test_support")
        self.test_query = config_obj.get("test_query")
        self.batch_size = config_obj.get("batch_size")

        # Learning Rates
        self.meta_lr = config_obj.get("meta_lr")
        self.task_lr = config_obj.get("task_lr")
        self.reduce_lr_rate = config_obj.get("reduce_lr_rate")
        self.patience = config_obj.get("patience")

        # Train Iter
        self.num_verbose_interval = config_obj.get("num_verbose_interval")
        self.num_task_train = config_obj.get("num_task_train")
        self.num_meta_train = config_obj.get("num_meta_train")

        self.test_agent = config_obj.get("test_agent")

        self.init_tk_params()
        self.init_tensorboard_params()
        self.init_models()

        # Logger
        formatter = logging.Formatter('%(message)s')

        fn = logging.FileHandler(
            filename=self.base_dir + 'logger.log', mode='w')
        fn.setLevel(logging.INFO)
        fn.setFormatter(formatter)

        self.logger = logging.getLogger('Ganabi Agents')
        self.logger.addHandler(fn)

        # Others
        self.best_eval_acc = 0.0  # controls model saving

    def init_tensorboard_params(self):
        #  Summary Writer for Tensorboard
        current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.base_dir = 'result/{}/{}/'.format(self.test_agent, current_time)
        self.log_dir = self.base_dir + 'logs/'
        self.save_path = self.base_dir + 'ckpt/'
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path, exist_ok=True)
        self.summary_writer = tf.summary.create_file_writer(self.log_dir)

    def init_tk_params(self):
        self.task_lr_schedule = tk.optimizers.schedules.ExponentialDecay(
            self.task_lr,  # initial_lr
            decay_steps=self.patience,
            decay_rate=self.reduce_lr_rate,
            staircase=True
        )

        self.meta_lr_schedule = tk.optimizers.schedules.ExponentialDecay(
            self.meta_lr,  # initial_lr
            decay_steps=self.patience,
            decay_rate=self.reduce_lr_rate,
            staircase=True
        )

        self.task_loss_op = tk.losses.SparseCategoricalCrossentropy()
        self.task_optimizer = tk.optimizers.SGD(
            self.task_lr_schedule, clipvalue=10)
        self.task_train_loss = tk.metrics.Mean(name='task_train_loss')
        self.task_train_accuracy = tk.metrics.SparseCategoricalAccuracy(
            name='task_train_accuracy')

        # Meta specific
        self.meta_loss_op = tk.losses.SparseCategoricalCrossentropy()
        self.meta_optimizer = tk.optimizers.Adam(
            self.meta_lr_schedule, clipvalue=10, amsgrad=True)
        self.meta_train_loss = tk.metrics.Mean(name='meta_train_loss')
        self.meta_train_accuracy = tk.metrics.SparseCategoricalAccuracy(
            name='meta_train_accuracy')

    def init_models(self):
        '''
        Build / Instantiate TF Keras Models
        '''

        # Build models
        if self.dataset == 'omniglot':
            self.model = models.SimpleModel(self.num_classes)
            self.task_models = [models.SimpleModel(self.num_classes)
                                for _ in range(self.num_tasks)]
            input_dim = (self.num_classes, 28, 28, 1)
        elif self.dataset == 'ganabi':
            self.model = models.NewGanabiModel(model_name="Meta")
            self.task_models = [models.NewGanabiModel(model_name="Task{}".format(i))
                                for i in range(self.num_tasks)]
            input_dim = (1, 658)
        else:
            raise("Unknown dataset {}. No appropriate model architechure.".format(
                self.dataset))

        # Meta Model
        self.model.build(input_dim)

        # Task Models
        for i, model in enumerate(self.task_models):
            self.task_models[i].build(input_dim)

        print(self.model.summary())

    def save_gin_config(self, config_file):
        shutil.copyfile(config_file, self.base_dir + 'config.gin')

    @tf.function
    def train_task(self, x_support, y_support, x_query, y_query, task, model):
        # Retrace Makes the code 20 times slower
        print("######################### Retrace Train Task {} #########################".format(task))
        # print(x_support.shape, y_support.shape, x_query.shape, y_query.shape)

        for s_shot in range(x_support.shape[0]):
            # convert ragged tensor to normal tensor
            X = x_support[s_shot]
            Y = y_support[s_shot]

            # Step 1: Forward Pass
            with tf.GradientTape() as task_tape:
                predictions = model(X)
                loss = self.task_loss_op(Y, predictions)

            grads = task_tape.gradient(
                loss, model.trainable_variables)

            # Step 2: Update params
            self.task_optimizer.apply_gradients(
                zip(grads, model.trainable_variables))

        # Query Set
        for q_shot in range(x_query.shape[0]):
            X = x_query[q_shot]
            Y = y_query[q_shot]

            # Step 1: Forward Pass
            with tf.GradientTape() as task_tape:
                predictions = model(X)
                loss = self.task_loss_op(Y, predictions)

            grads = task_tape.gradient(
                loss, model.trainable_variables)

            # Step 2: Record Gradients for Meta Gradients
            self.task_train_loss(loss)
            self.task_train_accuracy(Y, predictions)

        return grads

    @tf.function
    def train_meta(self, tasks_gradients):
        print("######################### Retrace Train Meta #########################")

        # Step 3 : get gFOMAML
        meta_gradients = []
        for i in range(len(tasks_gradients[0])):
            meta_grads = []
            for task in range(0, self.num_tasks):
                meta_grads.append(tasks_gradients[task][i])

            tf.stack(meta_grads)
            meta_grads = tf.math.reduce_mean(meta_grads, axis=0)
            meta_gradients.append(meta_grads)

        # Apply Gradient on meta model
        self.meta_optimizer.apply_gradients(zip(meta_gradients,
                                                self.model.trainable_variables))
        return meta_gradients

    @tf.function
    def eval_task(self, x_support, y_support, x_query, y_query, task, model):
        # Retrace Makes the code 20 times slower
        print("######################### Retrace Eval Task {} #########################".format(task))

        for s_shot in range(x_support.shape[0]):
            # convert ragged tensor to normal tensor
            X = x_support[s_shot]
            Y = y_support[s_shot]

            # Step 1: Forward Pass
            with tf.GradientTape() as task_tape:
                predictions = model(X)
                loss = self.task_loss_op(Y, predictions)

            grads = task_tape.gradient(
                loss, model.trainable_variables)

            # Step 2: Update params
            self.task_optimizer.apply_gradients(
                zip(grads, model.trainable_variables))

        # Query Set
        for q_shot in range(x_query.shape[0]):
            X = x_query[q_shot]
            Y = y_query[q_shot]

            # Step 1: Forward Pass
            with tf.GradientTape() as task_tape:
                predictions = model(X)
                loss = self.task_loss_op(Y, predictions)

            # Step 2: Record Gradients for Meta Gradients
            self.meta_train_loss(loss)
            self.meta_train_accuracy(Y, predictions)

    def train_step(self, train_batch, step):
        # Reset Weights
        self.reset_task_weights()
        # Train Task
        tasks_gradients = []
        for task in range(self.num_tasks):
            x_support, y_support, x_query, y_query = train_batch[task]
            grads = self.train_task(x_support,
                                    y_support,
                                    x_query,
                                    y_query,
                                    task,
                                    self.task_models[task])
            tasks_gradients.append(grads)

        # Train Meta
        meta_grads = self.train_meta(tasks_gradients)

        # Record Metrics

        if step % (self.num_verbose_interval / 5) == 0:
            train_loss, train_acc = self.record_metrics(step, is_train=True)

            # Print and Log
            template = 'Train  : Iteration {}, Loss: {:.3f}, Accuracy: {:.3f}'
            print(template.format(step, train_loss, train_acc))
            self.logger.warning(template.format(step, train_loss, train_acc))

    def eval_step(self, eval_batch, step):
        # Reset Weights
        self.reset_task_weights()

        # Eval Task
        for task in range(len(eval_batch)):
            x_support, y_support, x_query, y_query = eval_batch[task]
            self.eval_task(x_support,
                           y_support,
                           x_query,
                           y_query,
                           task,
                           self.task_models[task])

        # Record Metrics
        eval_loss, eval_acc = self.record_metrics(step, is_train=False)

        # Print and Log
        template = 'Test  : Iteration {}, Loss: {:.3f}, Accuracy: {:.3f}'
        print(template.format(step, eval_loss, eval_acc))
        self.logger.warning(template.format(step, eval_loss, eval_acc))

        return eval_loss, eval_acc

    def record_metrics(self, meta_step, is_train=True):
        '''
        Record Metrics at Tensorboard
        Includes: accuracy & loss at train or eval phase
        '''
        if is_train:
            # Record & Reset train loss & train acc
            train_loss = self.task_train_loss.result()
            train_acc = self.task_train_accuracy.result() * 100
            with self.summary_writer.as_default():
                tf.summary.scalar('train_loss', train_loss, step=meta_step)
                tf.summary.scalar('train_accuracy', train_acc, step=meta_step)
            self.task_train_loss.reset_states()
            self.task_train_accuracy.reset_states()

            return train_loss, train_acc
        else:
            # Record & Reset eval loss & eval acc
            eval_loss = self.meta_train_loss.result()
            eval_acc = self.meta_train_accuracy.result() * 100
            with self.summary_writer.as_default():
                tf.summary.scalar('eval_loss', eval_loss, step=meta_step)
                tf.summary.scalar('eval_accuracy', eval_acc, step=meta_step)
            self.meta_train_loss.reset_states()
            self.meta_train_accuracy.reset_states()

            return eval_loss, eval_acc

    def reset_task_weights(self):
        '''
        Reset all trainable variables in the task model to be equivalent to meta model

        Reason to not place this inside train_fomaml / eval_fomaml
        => Cannot set_weights in a @tf.function
        '''
        for i, model in enumerate(self.task_models):
            self.task_models[i].set_weights(self.model.get_weights())

    def train_manager(self, data_generator):
        """
        High Level Overview of training MAML
        """

        start_time = time.time()
        for meta_step in range(self.num_meta_train):
            # Train

            # tmp = time.time()
            train_batch = data_generator.next_batch(is_train=True)
            # print("Batch Time {}".format(time.time() - tmp))

            # tmp = time.time()
            self.train_step(train_batch, meta_step)
            # print("Train Time {}".format(time.time() - tmp))

            # Eval
            if meta_step % self.num_verbose_interval == 0:
                # Eval
                eval_batch = data_generator.next_batch(is_train=False)
                eval_loss, eval_acc = self.eval_step(eval_batch, meta_step)

                # Save model
                if self.best_eval_acc < eval_acc:
                    self.best_eval_acc = eval_acc
                    self.model.save_weights(
                        self.save_path + "/{}-weights.h5".format(meta_step))

                # Print
                template = 'Time to finish {} Meta Updates: {:.3f}'
                print(template.format(self.num_verbose_interval,
                                      (time.time() - start_time)))
                self.logger.warning(template.format(self.num_verbose_interval,
                                                    (time.time() - start_time)))
                start_time = time.time()
