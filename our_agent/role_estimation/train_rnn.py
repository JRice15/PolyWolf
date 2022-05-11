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

from role_estimation.data_loader import read_logs, filter_by_role

# modifiable
N_PLAYERS = 15
BATCHSIZE = 2
N_GAMES = 10
VAL_SIZE = 1
INPUT_FEATURES = ["agent_id", "target_id"]
N_HIDDEN_UNITS = 128

# don't modify
N_INPUT_FEATURES = len(INPUT_FEATURES)
ROLE_LIST = sorted(list(ROLES_15_PLAYER.keys()))
N_ROLES = len(ROLE_LIST)

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
        log_df, roles_df = read_logs(sim_dir)

        X_all.append(log_df)
        Y_all.append(roles_df)
    
    return X_all, Y_all


def build_batch(X, Y, my_agent_id, game, batchsize=BATCHSIZE):
    """
    args:
        X, Y: raw batch of data. X is list of df, Y is np.absarray
        game: index of game (0 to 99)
    """
    # y_batch = Y[:,game]
    # my_role_ints = y_batch[np.arange(len(my_agent_id)), my_agent_id]
    # my_role_onehot = tf.one_hot(my_role_ints, depth=N_ROLES)
    # my_roles = [ROLE_LIST[i] for i in my_role_ints]
    
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
        df = df[INPUT_FEATURES].fillna(value=0.0)
        batch_features.append(df.to_numpy())

    batch_targets = np.array(batch_targets)
    batch_features = pad_sequences(batch_features, dtype="float64")
    batch_my_roles = np.array(batch_my_roles)

    inputs = {
        "features": batch_features,
        "my_role": batch_my_roles,
    }

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
val_agent_id = np.random.randint(N_PLAYERS, size=VAL_SIZE)
VAL_INPUTS, VAL_TARGETS = build_batch(X, Y, val_agent_id, game=0, batchsize=VAL_SIZE)

for epoch in range(100):
    print("\n*** Epoch", epoch, "***")
    # get `batchsize` games
    X, Y = get_simsets(num=BATCHSIZE)
    # X: df with multiindex for utterances in games
    # Y: array with shape (batchsize, 100, n_roles)

    # keep track of game states over the sim
    game_states = np.zeros((BATCHSIZE, 1, N_HIDDEN_UNITS))

    # keep final preds
    final_preds = []
    final_targets = []

    # choose random agent to play as
    my_agent_id = np.random.randint(N_PLAYERS, size=BATCHSIZE)+1

    # iterate games 0 through 99
    prog_bar = tqdm(range(N_GAMES), ncols=100)
    for game in prog_bar:
        inputs, targets = build_batch(X, Y, my_agent_id, game)

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
            # average over number of players
            loss_value /= N_PLAYERS

        grads = tape.gradient(loss_value, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))

        # Update training metric.
        update_metric(train_acc_metric, targets, preds)

        # show train loss in progress bar
        prog_bar.set_postfix({"train loss": loss_value.numpy()})

        # game_states = np.concatenate() TODO

    print("Mean train predictions per role (in final game):")
    final_preds = tf.nn.softmax(np.stack(final_preds, axis=0), axis=-1).numpy().sum(axis=0).mean(axis=0)
    print(pd.DataFrame([final_preds], columns=sorted(list(ROLES_15_PLAYER.keys()))))

    # Display metrics at the end of each epoch.
    train_acc = train_acc_metric.result()
    train_acc_metric.reset_states()
    print("  Epoch train acc:", train_acc.numpy())

    val_preds = model(VAL_INPUTS)
    update_metric(val_acc_metric, VAL_TARGETS, val_preds)
    val_acc = val_acc_metric.result()
    val_acc_metric.reset_states()
    print("  Epoch val acc:", val_acc.numpy())
