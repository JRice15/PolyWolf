# AIWolfPy

Create python agents that can play Werewolf, following the specifications of the [AIWolf Project](http://aiwolf.org)

This has been forked from the official repository by the AIWolf project, and was originally created by [Kei Harada](https://github.com/k-harada).

# Conda Environment
I (jr) created a conda environment file to the specs of the python packages on the contest server (http://aiwolf.org/python_modules). You can create the env like the following, if you have conda set up already:

`conda env create -n aiwolf -f env.yml`

And then to activate:

`conda activate aiwolf`

# Running the agent and the server locally:
* Get AIWolf server platform (already included in this repo, in `AIWolf-ver0.6.3`)
	* Don't forget that the local AIWolf server requires JDK 11+
* Start the server with `./StartServer.sh`
	* This runs a Java application. Select the number of players, the connection port, and press "Connect".
* Run python agents from this repository, with the command: `./python_sample.py -h localhost -p [port]`
	* You can run them in the background by adding ` &` to the end of the command, so that you don't have to open N terminals.
* On the server application, press "Start Game".
  * The server application will print the log to the terminal, and also to the application window. Also, a log file will be saved on "./log".
* You can see a fun visualization using the "log viewer" program.

* Run `./AutoStarter.sh` to simulate games automatically with no GUI inputs (configured in `AutoStart.ini`)

# Running the agent on the AIWolf competition server:
* After you create your account in the competition server, make sure your client's name is the same as your account's name.
* The python packages available at the competition server are listed in this [page](http://aiwolf.org/python_modules)
* You can expect that the usual packages + numpy, scipy, pandas, scikit-learn are available.
	* Make sure to check early with the competition runners, specially if you want to use something like an specific version of tensorflow.
	* The competition rules forbid running multiple threads. Numpy and Chainer are correctly set-up server side, but for tensorflow you must make sure that your program follows this rule. Please see the following [post](http://aiwolf.org/archives/1951)
* For more information, a tutorial from the original author of this package can be seen in this [slideshare](https://www.slideshare.net/HaradaKei/aiwolfpy-v049) (in Japanese).
