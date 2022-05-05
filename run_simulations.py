import argparse
import subprocess
from datetime import datetime
import os
import random
import sys

# add the root dir to the path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from analyze_logs import analyze_logs


ALL_AGENTS = {
    "SampleJava": "java,org.aiwolf.sample.player.SampleRoleAssignPlayer",
    "SamplePy": f"python,{ROOT}/sample_python_agent/start.py",
    "HALU": f"python,{ROOT}/other_agents/HALU/HALUemon.py",
    "OKAMI": f"python,{ROOT}/other_agents/OKAMI/OKAMI.py",
    "Takeda": "java,org.aiwolf.takeda.TakedaRoleAssignPlayer",
    "TOKU": "java,org.aiwolf.TOKU.TOKURoleAssginPlayer",
    "Tomato": "java,com.gmail.toooo1718tyan.Player.RoleAssignPlayer",
}

CONFIG_FORMAT = """
lib={ROOT}/./AIWolf-ver0.6.3/
log={ROOT}/sims/{sim_name}/logs/
port=10000
game={games}
view=false
#C#=PATH_TO_C#_CLIENT_STARTER
setting={ROOT}/AIWolf-ver0.6.3/SampleSetting.cfg
#agent=5

{agents}
"""

# classpath elements
CLASSPATH_LIST = [
    # server files
    "{ROOT}/AIWolf-ver0.6.3/aiwolf-server.jar",
    "{ROOT}/AIWolf-ver0.6.3/aiwolf-common.jar",
    "{ROOT}/AIWolf-ver0.6.3/aiwolf-client.jar",
    "{ROOT}/AIWolf-ver0.6.3/aiwolf-viewer.jar",
    "{ROOT}/AIWolf-ver0.6.3/jsonic-1.3.10.jar",
    # agent jars (all are included regardless of it they are used, since it doesn't hurt)
    "{ROOT}/other_agents/TakedaAgent/takedaAgent.jar",
    "{ROOT}/other_agents/TeamSashimi/SashimiAgent.jar",
    "{ROOT}/other_agents/TeamTomato/TomatoAgent.jar",
    "{ROOT}/other_agents/TOKU/bin",
]


def run_sim(sim_name, ARGS):
    os.makedirs(f"sims/{sim_name}", exist_ok=True)

    # choose n agents
    selected_agents = random.choices(list(ALL_AGENTS.keys()), k=ARGS.agents)
    # format them
    selected_agents = [f"{name}{i},{ALL_AGENTS[name]}" for i,name in enumerate(selected_agents)]
    selected_agents_str = "\n".join(selected_agents)

    # config file contents
    config = CONFIG_FORMAT.format(sim_name=sim_name, games=ARGS.games, 
                agents=selected_agents_str, ROOT=ROOT)

    config_filename = f"sims/{sim_name}/config.ini"
    with open(config_filename, "w") as f:
        f.write(config)

    classpath = ":".join(CLASSPATH_LIST).format(ROOT=ROOT)
    command = f"java -cp {classpath} org.aiwolf.ui.bin.AutoStarter {config_filename}"

    subprocess.run(command, shell=True)

    # signal file that sim completed
    with open(f"sims/{sim_name}/sim_complete.txt", "w") as f:
        f.write(datetime.now().isoformat())

    analyze_logs(f"sims/{sim_name}/logs/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name",default="random",help="name to save these sims under")
    parser.add_argument("--sims",type=int,default=1,help="number of randomized n-game sims to run")
    parser.add_argument("--games",type=int,default=100,help="number of game per sim to run")
    parser.add_argument("--agents",type=int,default=15,help="number of agents, 5 or 15")
    ARGS = parser.parse_args()


    for _ in range(ARGS.sims):
        sim_name = "{}/sim_{}".format(ARGS.name, datetime.now().isoformat())
        run_sim(sim_name, ARGS)



if __name__ == "__main__":
    main()
