import glob
import os
import sys
import random

from tqdm import tqdm
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Model, callbacks, layers
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

from const import ROLES_5_PLAYER, ROLES_15_PLAYER

from role_estimation.data_loader import read_logs


INPUT_FEATURES = ["agent_id", "target_id"]
N_INPUT_FEATURES = len(INPUT_FEATURES)
BATCHSIZE = 2
N_ROLES = len(ROLES_15_PLAYER.keys())

"""
Build RNN model
"""
# unknown number of timesteps, each with n features
input_shape = (None, N_INPUT_FEATURES,)
inpt = layers.Input(input_shape, batch_size=BATCHSIZE)

gamestate_lstm = layers.LSTM(
        units=128,
        return_sequences=True, # return predictions for every timestep
        stateful=True, # means each batch is a continuation of the previous, until reset_state() is called on this layer
    )

# learn time-dependant features
rolepred_lstm = layers.GRU(
        units=64,
        stateful=False,
    )

# update gamestate
# gamestate = gamestate_lstm(inpt)
# compute time-independant features for each timestep
# x = layers.Conv1D(64, kernel_size=1)(inpt)
# x = layers.ReLU()(x)
# x = layers.Concatenate(axis=-1)([gamestate, x])
x = inpt
x = rolepred_lstm(x)

x = layers.Dense(N_ROLES)(x)
# don't use softmax when loss is from logits
# x = layers.Activation('softmax')(x)

model = Model(inpt, x)

model.summary()

"""
data loader
"""

def get_simsets(num=8):
    sim_dirs = glob.glob(f"{REPO_ROOT}/sims/15player_100game/random/*/logs/")
    sim_dirs = random.choices(sim_dirs, k=num)
    X_all = []
    Y_all = []
    for sim_dir in sim_dirs:
        print("Loading", sim_dir)
        log_df, roles_df = read_logs(sim_dir)

        roles = sorted(list(ROLES_15_PLAYER.keys()))
        roles_int_df = roles_df.applymap(roles.index)

        TARGET_AGENT = np.random.randint(1,16) # agent we are predicting

        X = log_df[INPUT_FEATURES]
        Y = roles_int_df[TARGET_AGENT]

        X_all.append(X)
        Y_all.append(Y)
    
    return X_all, Y_all


"""
training loop
"""
optimizer = keras.optimizers.Adam(learning_rate=1e-3)
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

train_acc_metric = keras.metrics.SparseCategoricalAccuracy()
val_acc_metric = keras.metrics.SparseCategoricalAccuracy()

for epoch in range(100):
    print("Epoch", epoch)
    X, Y = get_simsets(num=BATCHSIZE)
    Y = np.array(Y).T
    prog_bar = tqdm(range(100), ncols=100)
    for game in prog_bar:
        x_batch = [x.loc[game].to_numpy() for x in X]
        x_batch = pad_sequences(x_batch, dtype="float64")
        y_batch = Y[game]

        print(".....")
        print(x_batch.shape)
        print(y_batch.shape)
        
        with tf.GradientTape() as tape:
            preds = model(x_batch, training=True)
            loss_value = loss_fn(y_batch, preds)
        grads = tape.gradient(loss_value, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))

        print(preds.shape)
        print(preds.numpy())

        # Update training metric.
        train_acc_metric.update_state(y_batch, preds)

        # Log every 200 batches.
        # if game % 10 == 0:
        #     print(f"  Game {game} loss: {loss_value}")
        prog_bar.set_postfix({"loss": loss_value.numpy()})

    # Display metrics at the end of each epoch.
    train_acc = train_acc_metric.result()
    print("  Epoch acc:", train_acc)

