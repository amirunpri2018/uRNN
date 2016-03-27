#!/usr/bin/env ipython
# 
# Functions to generate data.
#
# Lightly modified from the original, for TensorFlow and readability.

import numpy as np
import tensorflow as tf
import pdb

def generate_adding(T, num_examples):
    # STEPH: num_examples is n_train or n_test
    #   T is the length of the sequence
    #   that is to say, the size of a single training instance
    x = np.asarray(np.zeros((num_examples, T, 2)),
                   dtype=np.float32)
    x[:, :, 0] = np.asarray(np.random.uniform(low=0.,
                                            high=1.,
                                            size=(num_examples, T)),
                          dtype=np.float32)
    
    inds = np.asarray(np.random.randint(T/2, size=(num_examples, 2)))
    inds[:, 1] += T/2  
    # STEPH: [:, 0] is from 0 til T/2, [:, 1] is [:, 0] + T/2
    #   basically, these just pick out which two elements will be added together
    
    for i in range(int(num_examples)):
        x[i, inds[i, 0], 1] = 1.0
        x[i, inds[i, 1], 1] = 1.0
    # STEPH: x[:, :, 1] is 1 in the row of given by the relevant num_examples of inds
    #   x[:, :, 1] is otherwise all 0s
 
    y = (x[:, :, 0] * x[:, :, 1]).sum(axis=1)
    # STEPH: before summing, y would be shape: (num_examples, T)...
    #   then we sum over T, so this is just num_examples length
    y = np.reshape(y, (num_examples, 1))
    # STEPH: now its shape is (num_examples, 1)
    #   this is: for each example in num_examples, it's the sum of two elements from
    #   the training instance (size T)...

    return (x, y)

def generate_memory(T, num_examples, seq_len=10):
    # in practice, seq_len is seemingly always 10
    seq = np.random.randint(1, high=9, size=(num_examples, seq_len))
    # STEPH: the sequence to remember
    #   uncertain why training examples are now dimension 0, but OK it gets
    #   transposed at the end... (probably to make concatenating easier?)
    zeros1 = np.zeros((num_examples, T-1))
    # STEPH: T-1 zeros
    zeros2 = np.zeros((num_examples, T))
    # STEPH: T zeros
    marker = 9 * np.ones((num_examples, 1))
    # STEPH: 1 set of 9s ('start reproducing sequence' marker)
    seq_zeros = np.zeros((num_examples, seq_len))
    # STEPH: length-of-sequence set of zeros

    x = np.concatenate((seq, zeros1, marker, seq_zeros), axis=1).astype('int32')
    # STEPH: the full input is: sequence, T-1 zeros, special marker,
    #   sequence-length zeros (empty category)

    # STEPH: So, to unify the implementation we can make it one-hot
    x_onehot = np.zeros(shape=list(x.shape) + [10])
    # STEPH: this is inefficient but I feel very unwell and can make it smarter later
    # TODO: make smarter
    for (n, example) in enumerate(x):
        # training example, now we set values
        x_onehot[n, xrange(len(example)), example] = 1

    y = np.concatenate((seq_zeros, zeros2, seq), axis=1).astype('int32')
    # STEPH: desired output is: T + length-of-seq sequence zeros, then sequence
   
    return (x_onehot, y)

class ExperimentData(object):
    def __init__(self, N, batch_size, experiment, T):
        self.N = N
        self.batch_size = batch_size
        if experiment == 'adding':
            self.x, self.y = generate_adding(T, N)
            self.dtype = tf.float32
            self.input_size = 2
            self.sequence_length = T
        elif experiment == 'memory':
            self.x, self.y = generate_memory(T, N, seq_len=10)
            self.dtype = tf.int32
            self.input_size = 10
            self.sequence_length = self.x.shape[1]      # this is probably T+20
        else:
            raise NotImplementedError
    def shuffle(self):
        permutation = np.random.permutation(self.N)
        self.x = self.x[permutation]
        self.y = self.y[permutation]
    def make_placeholders(self):
        placeholder_x = tf.placeholder(self.dtype, [self.batch_size] + list(self.x.shape[1:]))
        placeholder_y = tf.placeholder(self.dtype, [self.batch_size] + list(self.y.shape[1:]))
        return placeholder_x, placeholder_y
    def get_batch(self, i):
        batch_x = self.x[i * self.batch_size : (i + 1) * self.batch_size]
        batch_y = self.y[i * self.batch_size : (i + 1) * self.batch_size]
        return batch_x, batch_y
    # TODO: iterator for grabbing batches