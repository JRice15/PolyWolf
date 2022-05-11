from argparse import ArgumentParser

from aiwolf import AbstractPlayer, TcpipClient

from roles.role_assign_wrapper import RoleAssignPlayer

from const import REPO_ROOT, AGENT_ROOT


if __name__ == "__main__":
    
    agent = RoleAssignPlayer()

    parser = ArgumentParser(add_help=False)
    parser.add_argument("-p", type=int, action="store", dest="port", required=True)
    parser.add_argument("-h", type=str, action="store", dest="hostname", required=True)
    parser.add_argument("-r", type=str, action="store", dest="role", default="none")
    parser.add_argument("-n", type=str, action="store", dest="name", default="PolyWolf")
    input_args = parser.parse_args()
    
    TcpipClient(
        agent, 
        input_args.name, 
        input_args.hostname, 
        input_args.port, 
        input_args.role
    ).connect()
