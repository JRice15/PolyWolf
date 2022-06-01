# Sample AIWolf Python agent using aiwolf package
Sample AIWolf agent written in Python using [aiwolf package](https://github.com/AIWolfSharp/aiwolf-python).
## Prerequisites
* Python 3.8
* [aiwolf package]((https://github.com/AIWolfSharp/aiwolf-python)). 
You can install aiwolf package as follows,
```
pip install git+https://github.com/AIWolfSharp/aiwolf-python.git
```
## How to use
Suppose the AIWolf server at localhost is waiting a connection from an agent on port 10000.
You can connect this sample agent to the server as follows,
```
python start.py -h locahost -p 10000 -n name_you_like
```
If you get the error `socket.gaierror: [Errno 8] nodename nor servname provided, or not known` make sure you have the line `127.0.0.1	localhost` in your `/etc/hosts` and change the line `self.sock.connect((self.host, self.port))` to `self.sock.connect(('localhost', self.port))`.
