#!/bin/bash

# lstm instead of gru
python3 train_rnn.py --rnn-type lstm

# multiple layers
python3 train_rnn.py --n-layers 2

# large learning rate (I read it could maybe help with sparse data)
python3 train_rnn.py --lr 0.1

# larger batchsize
python3 train_rnn.py --n-hidden-units 128 --batchsize 128