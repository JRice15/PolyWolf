import glob
import os
import random
import sys
import time
import argparse
from pprint import pprint

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.keras import backend as K
from tensorflow.keras import callbacks, layers
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm


class MyConcat(layers.Layer):
    """
    concatenate a sequence, shape (batchsize, variable timesteps, features),
    with a vector, shape (batchsize, length)
    returns:
        sequence, shape (batchsize, timesteps, features + length)
    """

    def call(self, x):
        sequence, vector = x
        timesteps = tf.shape(sequence)[-2]
        vec_size = vector.shape[-1]
        vector = tf.reshape(vector, (-1, 1, vec_size))
        vector = tf.tile(vector, [1, timesteps, 1])
        result = tf.concat([sequence, vector], axis=-1)
        return result
