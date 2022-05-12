import glob
import os
import random
import sys
import time

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

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

from const import ROLES_5_PLAYER, ROLES_15_PLAYER

from role_estimation.data_loader import (N_INPUT_FEATURES, filter_by_role,
                                         one_hot_encode, read_logs)

# modifiable
N_PLAYERS = 15
BATCHSIZE = 16
VAL_SIZE = 32
N_HIDDEN_UNITS = 512
DROP_SKIPS = True

# don't modify
ROLE_LIST = sorted(list(ROLES_15_PLAYER.keys()))
N_ROLES = len(ROLE_LIST)
N_GAMES = 100

"""
Build RNN model
"""

gamestate_gru = layers.GRU(
    units=N_HIDDEN_UNITS,
    name="gamestate_gru"
)

# learn time-dependant features
rolepred_gru = layers.GRU(
        units=N_HIDDEN_UNITS,
        name="rolepred_gru",
    )


# unknown number of timesteps, each with n features
inpt_features = layers.Input((None, N_INPUT_FEATURES,), name="features")
# one-hot role encoding
inpt_role = layers.Input((N_ROLES,), name="my_role")

# result of GRU from previous games
# inpt_previous_states = layers.Input((None, N_HIDDEN_UNITS), name="prev_states")

# gamestate = gamestate_gru(inpt_previous_states)
learned_features = rolepred_gru(
                        inpt_features, 
                        # initial_state=gamestate
                )

full_features = layers.Concatenate(axis=-1)([learned_features, inpt_role])

# one output prediction per agent
# no softmaxes here because from_logits=True in loss
outputs = {}
for i in range(N_PLAYERS):
    x = layers.Dense(N_ROLES, name=f"agent{i}_pred")(full_features)
    outputs[f"agent{i}_pred"] = x 
outputs["game_features"] = full_features

model = Model(
            [
                inpt_features, 
                inpt_role, 
                # inpt_previous_states
            ], 
            outputs
        )

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
        print("  loading", sim_dir)
        log_df, roles_df = read_logs(sim_dir,
                                drop_skips=DROP_SKIPS)

        X_all.append(log_df)
        Y_all.append(roles_df)
    
    return X_all, Y_all


def build_batch(X, Y, my_agent_id, game, batchsize=BATCHSIZE):
    """
    args:
        X, Y: raw batch of data. X is list of df, Y is np.absarray
        game: index of game (0 to 99)
    """    
    batch_targets = []
    batch_features = []
    batch_my_roles = []
    for batch_index in range(batchsize):
        # get ground-truth roles
        y_batch = Y[batch_index].loc[game]
        # print(y_batch)
        batch_targets.append(y_batch.apply(lambda x: ROLE_LIST.index(x)).to_numpy())

        # get role
        my_role = y_batch[my_agent_id[batch_index]]
        my_role_onehot = tf.one_hot(ROLE_LIST.index(my_role), depth=N_ROLES).numpy()
        batch_my_roles.append(my_role_onehot)

        # get X features
        df = X[batch_index].loc[game]
        df = filter_by_role(df, my_role)
        # df = df[INPUT_FEATURES].fillna(value=-1)
        arr = one_hot_encode(df)
        batch_features.append(arr)

    batch_features = pad_sequences(batch_features, dtype=K.floatx())
    batch_my_roles = tf.constant(batch_my_roles)

    inputs = {
        "features": batch_features,
        "my_role": batch_my_roles,
    }

    batch_targets = tf.constant(batch_targets)

    return inputs, batch_targets


"""
training loop
"""

def update_metric(metric, y, preds):
    for i in range(N_PLAYERS):
        metric.update_state(y[:,i], preds[f"agent{i}_pred"])    

optimizer = keras.optimizers.Adam(learning_rate=1e-3)
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

train_acc_metric = keras.metrics.SparseCategoricalAccuracy()
val_acc_metric = keras.metrics.SparseCategoricalAccuracy()

X, Y = get_simsets(num=VAL_SIZE)
val_agent_id = np.random.randint(N_PLAYERS, size=VAL_SIZE)+1
VAL_INPUTS, VAL_TARGETS = build_batch(X, Y, val_agent_id, game=0, batchsize=VAL_SIZE)


best_val_loss = np.inf
best_epoch = -1

for epoch in range(1000):
    print("\n*** Epoch", epoch, "***")
    starttime = time.perf_counter()

    # get `batchsize` games
    X, Y = get_simsets(num=BATCHSIZE)
    # X: df with multiindex for utterances in games
    # Y: array with shape (batchsize, 100, n_roles)

    # keep track of game states over the sim
    game_states = np.zeros((BATCHSIZE, 1, N_HIDDEN_UNITS))

    # keep final preds
    final_preds = []
    final_targets = []

    # track stats
    game_lens = []

    # choose random agent to play as
    my_agent_id = np.random.randint(N_PLAYERS, size=BATCHSIZE)+1

    # iterate games 0 through 99
    prog_bar = tqdm(range(N_GAMES), ncols=100)
    for game in prog_bar:
        inputs, targets = build_batch(X, Y, my_agent_id, game)

        game_lens.append(inputs["features"].shape[1])
        # print("  seq len:", inputs["features"].shape[1])

        with tf.GradientTape() as tape:
            preds = model(inputs, training=True)
            # sum losses for each prediction
            loss_value = 0
            for i in range(N_PLAYERS):
                pred_i = preds[f"agent{i}_pred"]
                if game == N_GAMES-1:
                    final_preds.append(pred_i)
                loss_value += loss_fn(targets[:,i], pred_i)

        grads = tape.gradient(loss_value, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))

        # Update training metric.
        update_metric(train_acc_metric, targets, preds)

        # show train loss in progress bar
        prog_bar.set_postfix({"train loss": loss_value.numpy()})

        # game_states = np.concatenate() TODO

    print("  seq lens:")
    print("    avg:", np.mean(game_lens))
    print("    max:", np.max(game_lens))

    print("  Mean train predictions per role (in final game):")
    final_preds = tf.nn.softmax(np.stack(final_preds, axis=0), axis=-1).numpy().sum(axis=0).mean(axis=0)
    print(pd.DataFrame([final_preds], columns=sorted(list(ROLES_15_PLAYER.keys()))))

    # Display metrics at the end of each epoch.
    train_acc = train_acc_metric.result()
    train_acc_metric.reset_states()
    print("  Train acc:", train_acc.numpy())

    # Validation metrics
    val_preds = model(VAL_INPUTS)
    val_loss = 0
    for i in range(N_PLAYERS):
        vpred_i = val_preds[f"agent{i}_pred"]
        val_loss += loss_fn(VAL_TARGETS[:,i], vpred_i)
    val_loss = val_loss.numpy()
    print("  Validation loss:", val_loss)

    update_metric(val_acc_metric, VAL_TARGETS, val_preds)
    val_acc = val_acc_metric.result()
    val_acc_metric.reset_states()
    print("  Validation acc:", val_acc.numpy())

    if val_loss < best_val_loss:
        print("  Best val loss achieved. Saving model...")
        best_val_loss = val_loss
        best_epoch = epoch
        model.save(
            "model.h5",
            save_format="h5",
        )
    
    print("  took", round(time.perf_counter() - starttime, 2), "secs")
