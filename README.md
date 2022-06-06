# PolyWolf
By Julian Rice, Arman Rafian, Trevor Kirkby, & Joel Valdovinos

A project for CSC 570: AI in Games with Dr. Canaan, at California Polytechnic State University.


## External Resource Acknowledgements
This is an agent capable of playing the social deduction game _Werewolf_, following the specifications of the [AIWolf Project](http://aiwolf.org). This repository has been forked from [the official repository by the AIWolf project](https://github.com/aiwolf/AIWolfPy), and was originally created by [Kei Harada](https://github.com/k-harada).

This repository includes the source code for a number of previous years' agents for simulation purposes, which can be found on the [AIWolf site](http://aiwolf.org/en/archives/2620). The following agents are included in `other_agents`:
* HALU
* Karma
* OKAMI
* TakedaAgent
* TeamSashimi
* TeamTomato
* TOKU
* TOT
Additionally, multiple sample agents provided by the compeitions organizers are included.

# Environment Setup
A conda environment file is included, which contains the specifications of all python packages needed to run our agent. You can create the environment like the following, if you have conda set up already:

`conda env create -n aiwolf -f env.yml`

And then to activate:

`conda activate aiwolf`


# Running The Agent

There are multiple components to the agent. To run the final product, `run_simulations.py` is the easiest interface. Run in the following manner:

`python3 run_simulations.py --sims N --games 100 --use PolyWolf --name demo`

This will run N simulations, of 100 games each, which will use a random selection of opponents and at least one copy of the PolyWolf agent. Logs will be output to `sims/15player_100game/demo`, and results will be printed to the screen when the sims complete.

To train the neural network yourself on our pre-generated logs, navigate to `our_agent/role_estimation` and run:

`python3 train_rnn.py --lr 0.1`

This script will save the best model to `model.h5`. A pretrained model is provided in `pretrained_model.h5`, which is what is loaded by the RNN estimator during gameplay. It trained for over 100 epochs. To use your trained model instead, rename it to overwrite `pretrained_model.h5`.
