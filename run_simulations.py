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
    # broken for some reason
    # "Sashimi": "java,jp.ac.tsukuba.s.s2020602.SashimiRoleAssignPlayer",
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

# load classpath
with open(f"{ROOT}/classpath_list.txt", "r") as f:
    CLASSPATH = f.readlines()
CLASSPATH = [x.strip() for x in CLASSPATH]
CLASSPATH = ":".join([x for x in CLASSPATH if len(x)])


def run_sim(sim_name, ARGS):
    os.makedirs(f"sims/{sim_name}", exist_ok=True)

    # hardcoded agents
    selected_agents = list(ARGS.use)
    still_needed = ARGS.agents - len(selected_agents)
    # choose n agents
    selected_agents += random.choices(list(ALL_AGENTS.keys()), k=still_needed)
    # format them
    selected_agents = [f"{name}{i},{ALL_AGENTS[name]}" for i,name in enumerate(selected_agents)]
    selected_agents_str = "\n".join(selected_agents)

    # config file contents
    config = CONFIG_FORMAT.format(sim_name=sim_name, games=ARGS.games, 
                agents=selected_agents_str, ROOT=ROOT)

    config_filename = f"sims/{sim_name}/config.ini"
    with open(config_filename, "w") as f:
        f.write(config)

    command = f"java -cp {CLASSPATH} org.aiwolf.ui.bin.AutoStarter {config_filename}"

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
    parser.add_argument("--use",nargs="+",default=(),help="include these specific agents (by name, duplicates allowed)")
    ARGS = parser.parse_args()

    for _ in range(ARGS.sims):
        sim_name = "{}/sim_{}".format(ARGS.name, datetime.now().isoformat())
        run_sim(sim_name, ARGS)



if __name__ == "__main__":
    main()
