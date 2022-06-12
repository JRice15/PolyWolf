#!/bin/bash

# lstm instead of gru
# python3 train_rnn.py --rnn-type lstm # It performed shockingly similar, skipping to the next test since I interrupted running after this one...

# multiple layers
# python3 train_rnn.py --n-layers 2 # Adding a layer really worked wonders! :)

# large learning rate (I read it could maybe help with sparse data)
#python3 train_rnn.py --lr 0.1 # Works even better than adding a layer, somehow.

# larger batchsize
#python3 train_rnn.py --n-hidden-units 128 --batchsize 128

python train_rnn.py --lr 0.1
