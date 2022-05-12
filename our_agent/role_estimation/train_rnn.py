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

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

from const import ROLES_5_PLAYER, ROLES_15_PLAYER

from role_estimation.data_loader import (N_INPUT_FEATURES, filter_by_role,
                                         one_hot_encode, read_logs)


parser = argparse.ArgumentParser()
parser.add_argument("--n-players",type=int,choices=(15,),default=15) # TODO allow 5 player
parser.add_argument("--batchsize",type=int,default=16)
parser.add_argument("--valsize",type=int,default=32)
parser.add_argument("--n-hidden-units",type=int,default=512)
parser.add_argument("--no-drop-skips",action="store_false",dest="drop_skips")
parser.add_argument("--reducelr-epochs",type=int,default=15)
parser.add_argument("--reducelr-factor",type=float,default=0.1)
parser.add_argument("--earlystopping-epochs",type=int,default=12)
ARGS = parser.parse_args()

pprint(vars(ARGS))

# don't modify
N_PLAYERS = ARGS.n_players
ROLE_LIST = sorted(list(ROLES_15_PLAYER.keys()))
N_ROLES = len(ROLE_LIST)
N_GAMES = 100

"""
Build RNN model
"""

gamestate_gru = layers.GRU(
    units=ARGS.n_hidden_units,
    name="gamestate_gru"
)

# learn time-dependant features
rolepred_gru = layers.GRU(
        units=ARGS.n_hidden_units,
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
        # print("  loading", sim_dir)
        log_df, roles_df = read_logs(sim_dir,
                                drop_skips=ARGS.drop_skips)

        X_all.append(log_df)
        Y_all.append(roles_df)
    
    return X_all, Y_all


def build_batch(X, Y, my_agent_id, game, batchsize=ARGS.batchsize):
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

optimizer = keras.optimizers.Adam(learning_rate=1e-3)
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

train_acc_metric = keras.metrics.SparseCategoricalAccuracy()
val_acc_metric = keras.metrics.SparseCategoricalAccuracy()

print("Loading val data...")
X, Y = get_simsets(num=ARGS.valsize)
val_agent_id = np.random.randint(N_PLAYERS, size=ARGS.valsize)+1
VAL_INPUTS, VAL_TARGETS = build_batch(X, Y, val_agent_id, game=0, batchsize=ARGS.valsize)

@tf.function(experimental_relax_shapes=True)
def train_step(inputs, targets):
    with tf.GradientTape() as tape:
        preds = model(inputs, training=True)
        # sum losses for each prediction
        loss_value = 0
        for i in range(N_PLAYERS):
            pred_i = preds[f"agent{i}_pred"]
            loss_value += loss_fn(targets[:,i], pred_i)

    grads = tape.gradient(loss_value, model.trainable_weights)
    optimizer.apply_gradients(zip(grads, model.trainable_weights))

    # Update training metric.
    for i in range(N_PLAYERS):
        train_acc_metric.update_state(targets[:,i], preds[f"agent{i}_pred"])    
    
    return loss_value, preds

@tf.function
def val_step(val_inputs, val_targets):
    val_preds = model(val_inputs)
    val_loss = 0
    for i in range(N_PLAYERS):
        vpred_i = val_preds[f"agent{i}_pred"]
        val_loss += loss_fn(val_targets[:,i], vpred_i)
        val_acc_metric.update_state(val_targets[:,i], vpred_i)    

    return val_loss


best_val_loss = np.inf
best_epoch = -1

for epoch in range(1000):
    print("\n*** Epoch", epoch, "***")
    starttime = time.perf_counter()

    """
    data prep
    """

    print("  loading data...")
    # get `batchsize` games
    X, Y = get_simsets(num=ARGS.batchsize)
    # X: df with multiindex for utterances in games
    # Y: array with shape (batchsize, 100, n_roles)

    # keep track of game states over the sim
    game_states = np.zeros((ARGS.batchsize, 1, ARGS.n_hidden_units))

    # keep final preds
    final_preds = []
    final_targets = []

    # track stats
    game_lens = []

    # choose random agent to play as
    my_agent_id = np.random.randint(N_PLAYERS, size=ARGS.batchsize)+1

    """
    train loop
    """

    print("  training...")
    # iterate games 0 through 99
    game_counter = tqdm(range(N_GAMES), ncols=100)
    for game in game_counter:
        inputs, targets = build_batch(X, Y, my_agent_id, game)

        game_lens.append(inputs["features"].shape[1])
        # print("  seq len:", inputs["features"].shape[1])

        loss_value, preds = train_step(inputs, targets)

        # save predictions of final game
        if game == N_GAMES-1:
            for i in range(N_PLAYERS):
                final_preds.append(preds[f"agent{i}_pred"])

        # show train loss in progress bar
        game_counter.set_postfix({"train loss": loss_value.numpy()})

        # game_states = np.concatenate() TODO

    """
    show metrics
    """

    print("  seq lens:")
    print("    avg:", np.mean(game_lens))
    print("    max:", np.max(game_lens))

    print("  Mean train predictions per role (in final game):")
    final_preds = tf.nn.softmax(np.stack(final_preds, axis=0), axis=-1).numpy().sum(axis=0).mean(axis=0)
    print(pd.DataFrame([final_preds], columns=sorted(list(ROLES_15_PLAYER.keys()))))

    # Val loss
    val_loss = val_step(VAL_INPUTS, VAL_TARGETS)
    val_loss = val_loss.numpy()
    print("  Validation loss:", val_loss)

    # Train and Val accuracies
    train_acc = train_acc_metric.result()
    train_acc_metric.reset_states()
    print("  Train acc:", train_acc.numpy())
    val_acc = val_acc_metric.result()
    val_acc_metric.reset_states()
    print("  Validation acc:", val_acc.numpy())

    """
    callbacks
    """

    # save model
    if val_loss < best_val_loss:
        print("  Best val loss achieved. Saving model...")
        best_val_loss = val_loss
        best_epoch = epoch
        model.save(
            "model.h5",
            save_format="h5",
        )
    
    # early stopping
    no_improvement_epochs = epoch - best_epoch
    if no_improvement_epochs >= ARGS.earlystopping_epochs:
        print("Early stopping:", no_improvement_epochs, "with no improvement")
        break

    # reduce learning rate on plateau
    if no_improvement_epochs > 0 and no_improvement_epochs % ARGS.reducelr_epochs == 0:
        lr = optimizer.learning_rate
        new_lr = lr * ARGS.reducelr_factor
        print("  Reducelr:", no_improvement_epochs, "epochs with no improvement, reducing lr to", new_lr.numpy())
        optimizer.learning_rate.assign(new_lr)

    print("  took", round(time.perf_counter() - starttime, 2), "secs")
