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
parser.add_argument("--sample-loss-freq",type=int,default=50)
parser.add_argument("--n-hidden-units",type=int,default=512)
parser.add_argument("--no-drop-skips",action="store_false",dest="drop_skips")
parser.add_argument("--lr",type=float,default=1e-3,help="initial learning rate")
parser.add_argument("--reducelr-epochs",type=int,default=5)
parser.add_argument("--reducelr-factor",type=float,default=0.1)
parser.add_argument("--earlystopping-epochs",type=int,default=12)
parser.add_argument("--ngames",default=100,type=int,help="don't override this unless you are just testing stuff")
ARGS = parser.parse_args()

pprint(vars(ARGS))

# don't modify
N_PLAYERS = ARGS.n_players
ROLE_LIST = sorted(list(ROLES_15_PLAYER.keys()))
N_ROLES = len(ROLE_LIST)
N_GAMES = ARGS.ngames

# sanity checks
assert ARGS.reducelr_epochs < ARGS.earlystopping_epochs
assert ARGS.reducelr_factor < 1.0

"""
Build RNN model
"""


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


def build_model():
    # gamestate_rnn = layers.GRU(
    #     units=ARGS.n_hidden_units,
    #     name="gamestate_gru"
    # )

    # learn time-dependant features
    rolepred_rnn = layers.GRU(
            units=ARGS.n_hidden_units,
            name="rolepred_gru",
            return_sequences=True,
        )


    # unknown number of timesteps, each with n features
    inpt_features = layers.Input((None, N_INPUT_FEATURES,), name="features")
    # one-hot role encoding
    inpt_role = layers.Input((N_ROLES,), name="my_role")
    # one-hot id encoding
    inpt_id = layers.Input((N_PLAYERS,), name="my_id")

    one_d_features = layers.Concatenate(axis=-1)([inpt_role, inpt_id])
    all_inpt_features = MyConcat()([inpt_features, one_d_features])

    # result of GRU from previous games
    # inpt_previous_states = layers.Input((None, N_HIDDEN_UNITS), name="prev_states")
    # gamestate = gamestate_rnn(inpt_previous_states)

    learned_features = rolepred_rnn(
                            all_inpt_features, 
                            # initial_state=gamestate
                    )

    full_features = MyConcat()([learned_features, one_d_features])
    # add a dimension
    full_features = layers.Reshape((-1, 1, full_features.shape[-1]))(full_features)

    # one output prediction per agent
    # no softmaxes here because from_logits=True in loss
    agent_preds = []
    for i in range(N_PLAYERS):
        x = layers.Dense(N_ROLES, name=f"agent{i}_pred")(full_features)
        agent_preds.append(x)
    
    agent_preds = layers.Concatenate(axis=-2, name="output_preds")(agent_preds)

    model = Model(
                [
                    inpt_features, 
                    inpt_role, 
                    inpt_id,
                    # inpt_previous_states
                ], 
                {
                    "preds": agent_preds,
                    "game_features": learned_features,
                }
            )
    return model


model = build_model()
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


def build_batch(X, Y, my_agent_ids, game, batchsize=ARGS.batchsize):
    """
    args:
        X, Y: raw batch of data. X is list of df, Y is np.absarray
        game: index of game (0 to 99)
    """    
    batch_targets = []
    batch_features = []
    batch_my_roles = []
    batch_my_ids = []
    for batch_index in range(batchsize):
        # get ground-truth roles
        roles_df = Y[batch_index].loc[game]
        # print(y_batch)
        batch_targets.append(roles_df.apply(lambda x: ROLE_LIST.index(x)).to_numpy())

        # get agent id
        my_id = my_agent_ids[batch_index]
        my_id_onehot = tf.one_hot(my_id-1, depth=N_PLAYERS).numpy()
        batch_my_ids.append(my_id_onehot)

        # get role
        my_role = roles_df[my_id]
        my_role_onehot = tf.one_hot(ROLE_LIST.index(my_role), depth=N_ROLES).numpy()
        batch_my_roles.append(my_role_onehot)

        # get X features
        df = X[batch_index].loc[game]
        df = filter_by_role(df, my_role)
        arr = one_hot_encode(df)
        batch_features.append(arr)

    batch_features = pad_sequences(batch_features, dtype=K.floatx())
    batch_my_roles = tf.constant(batch_my_roles)
    batch_my_ids = tf.constant(batch_my_ids)

    inputs = {
        "features": batch_features,
        "my_role": batch_my_roles,
        "my_id": batch_my_ids,
    }

    batch_targets = tf.constant(batch_targets)

    return inputs, batch_targets


"""
training loop
"""

optimizer = keras.optimizers.Adam(learning_rate=1e-3)
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

train_wholegame_acc_metric = keras.metrics.SparseCategoricalAccuracy()
val_wholegame_acc_metric = keras.metrics.SparseCategoricalAccuracy()
train_final_acc_metric = keras.metrics.SparseCategoricalAccuracy()
val_final_acc_metric = keras.metrics.SparseCategoricalAccuracy()

print("Loading val data...")
X, Y = get_simsets(num=ARGS.valsize)
val_agent_id = np.random.randint(N_PLAYERS, size=ARGS.valsize)+1
VAL_INPUTS, VAL_TARGETS = build_batch(X, Y, val_agent_id, game=0, batchsize=ARGS.valsize)

@tf.function(experimental_relax_shapes=True)
def train_step(inputs, targets):
    seq_len = tf.shape(inputs["features"])[-2]
    subsampled_seq_len = tf.math.ceil(seq_len / ARGS.sample_loss_freq)
    targets = tf.tile(tf.reshape(targets, (-1,1,N_PLAYERS)), [1,subsampled_seq_len,1])

    with tf.GradientTape() as tape:
        outputs = model(inputs, training=True)
        preds = outputs["preds"][:,::ARGS.sample_loss_freq]
        loss_value = loss_fn(targets, preds)

    grads = tape.gradient(loss_value, model.trainable_weights)
    optimizer.apply_gradients(zip(grads, model.trainable_weights))

    # Update training metric.
    train_wholegame_acc_metric.update_state(targets, preds)
    train_final_acc_metric.update_state(targets[:,-1], preds[:,-1])
    
    return loss_value, outputs

@tf.function
def val_step(inputs, targets):
    seq_len = tf.shape(inputs["features"])[-2]
    targets = tf.tile(tf.reshape(targets, (-1,1,N_PLAYERS)), [1,seq_len,1])

    outputs = model(inputs)
    preds = outputs["preds"]
    loss_value = loss_fn(targets, preds)

    val_wholegame_acc_metric.update_state(targets, preds)    
    val_final_acc_metric.update_state(targets[:,-1], preds[:,-1])

    return loss_value


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

    # keep maximum pred for each
    max_pred_probs = []
    final_preds = []

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

        train_loss, outputs = train_step(inputs, targets)
        train_loss = train_loss.numpy()

        # save predictions of final game
        if game == N_GAMES-1:
            pred_probs = tf.nn.softmax(outputs["preds"], axis=-1).numpy()
            pred_probs = np.squeeze(pred_probs)
            final_pred_probs = pred_probs[:,-1] # result is (batchsize, nplayers, nroles)
            final_preds.append(np.argmax(final_pred_probs, axis=-1))
            print("\n", pred_probs.shape)
            # fill predictions for self with zeros
            for i,a_id in enumerate(my_agent_id):
                pred_probs[i,:,a_id-1] = 0
            max_pred_probs.append(pred_probs.max(axis=(0,1,2)))


        # show train loss in progress bar
        game_counter.set_postfix({"train loss": train_loss})

        # game_states = np.concatenate() TODO

    """
    show metrics
    """

    print("  seq lens:")
    print("    avg:", np.mean(game_lens))
    print("    max:", np.max(game_lens))

    print("  Max pred probability per role (in final train game):")
    max_pred_probs = np.max(max_pred_probs, axis=0)
    print("   ", dict(zip(ROLE_LIST, max_pred_probs)))
    print("  Num predicted at end of final game for each class:")
    all_preds = np.concatenate(final_preds)
    unique, counts = np.unique(all_preds, return_counts=True)
    roles = [ROLE_LIST[x] for x in unique]
    print("   ", dict(zip(roles, counts)))

    # losses
    val_loss = val_step(VAL_INPUTS, VAL_TARGETS)
    val_loss = val_loss.numpy()
    print("  Loss:")
    print("    Train (subsampled):", train_loss)
    print("    Val (whole game):  ", val_loss)

    # accuracies
    print("  Accuracy:")
    print("    Train, wholegame:  ", train_wholegame_acc_metric.result().numpy())
    print("    Val, wholegame:    ", val_wholegame_acc_metric.result().numpy())
    print("    Train, end-of-game:", train_final_acc_metric.result().numpy())
    print("    Val, end-of-game:  ", val_final_acc_metric.result().numpy())


    train_wholegame_acc_metric.reset_states()
    train_final_acc_metric.reset_states()
    val_wholegame_acc_metric.reset_states()
    val_final_acc_metric.reset_states()

    """
    callbacks
    """

    # save model
    if val_loss < best_val_loss - 1e-6:
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
