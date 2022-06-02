import argparse
import glob
import os
import random
import re
import shutil
import subprocess
import sys
from datetime import datetime

# add the root dir to the path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from analyze_logs import analyze_logs

ALL_AGENTS = {
    "SampleJava": "java,org.aiwolf.sample.player.SampleRoleAssignPlayer",
    "SamplePy": f"python,{ROOT}/other_agents/sample_python_agent/start.py",
    "HALU": f"python,{ROOT}/other_agents/HALU/HALUemon.py",
    "OKAMI": f"python,{ROOT}/other_agents/OKAMI/OKAMI.py",
    "Takeda": "java,org.aiwolf.takeda.TakedaRoleAssignPlayer",
    "TOKU": "java,org.aiwolf.TOKU.TOKURoleAssginPlayer",
    "Tomato": "java,com.gmail.toooo1718tyan.Player.RoleAssignPlayer",
    "contrarian": f"python,{ROOT}/test/contrarian.py",
    "rando": f"python,{ROOT}/test/rando.py",
    "sheep": f"python,{ROOT}/test/sheep.py",
    "spamton": f"python,{ROOT}/test/spamton.py",
    "estimator_demo": f"python,{ROOT}/our_agent/rnn_estimator_demo.py",
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
    sim_name = re.sub(r":", "-", sim_name)
    os.makedirs(f"sims/{sim_name}", exist_ok=True)

    # hardcoded agents
    selected_agents = list(ARGS.use)
    # get roles if specified
    selected_roles = [a.split("=")[1] if len(a.split("=")) > 1 else None for a in selected_agents]
    selected_agents = [a.split("=")[0] for a in selected_agents]
    still_needed = ARGS.agents - len(selected_agents)
    # choose n agents
    selected_agents += random.choices(list(ALL_AGENTS.keys()), k=still_needed)
    # format them
    selected_agents = [f"{name}{i},{ALL_AGENTS[name]}" for i,name in enumerate(selected_agents)]
    for i,role in enumerate(selected_roles):
        if role is not None:
            selected_agents[i] = selected_agents[i] + "," + role
    selected_agents_str = "\n".join(selected_agents)

    # config file contents
    config = CONFIG_FORMAT.format(sim_name=sim_name, games=ARGS.games, 
                agents=selected_agents_str, ROOT=ROOT)

    config_filename = f"sims/{sim_name}/config.ini"
    with open(config_filename, "w") as f:
        f.write(config)

    command = f"java -cp {CLASSPATH} org.aiwolf.ui.bin.AutoStarter {config_filename}"

    subprocess.run(command, shell=True)

    logs = glob.glob(f"{ROOT}/sims/{sim_name}/logs/???.log")
    if len(logs) < ARGS.games:
        print("Only", len(logs), "found")
    else:
        # signal file that sim completed
        with open(f"{ROOT}/sims/{sim_name}/sim_complete.txt", "w") as f:
            f.write(datetime.now().isoformat())

        analyze_logs(f"sims/{sim_name}/logs/")


def clean_sims(simset_name):
    # remove sim dirs that did not complete their simulation
    for dirn in glob.glob(f"{ROOT}/sims/{simset_name}/sim_*/"):
        if not os.path.exists(dirn + "sim_complete.txt"):
            print("removing", dirn)
            shutil.rmtree(dirn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name",default="random",help="name to save these sims under")
    parser.add_argument("--sims",type=int,default=1,help="number of randomized n-game sims to run")
    parser.add_argument("--games",type=int,default=100,help="number of game per sim to run")
    parser.add_argument("--agents",type=int,default=15,help="number of agents, 5 or 15")
    parser.add_argument("--use",nargs="+",default=(),help="include these specific agents (by name, duplicates allowed)")
    parser.add_argument("--priority",type=int,default=0,help="priority to have the OS assign to this process (higher num means lower priority)")
    ARGS = parser.parse_args()

    try:
        old = os.nice(0)
        new = os.nice(ARGS.priority)
        print("Set niceness from", old, "to", new)
    except Exception as e:
        print("Error setting os.nice priority value:", e)

    simset_name = "{}player_{}game/{}".format(ARGS.agents, ARGS.games, ARGS.name)

    try:
        for _ in range(ARGS.sims):
            sim_name = simset_name + "/sim_{}".format(datetime.now().isoformat())
            run_sim(sim_name, ARGS)
    except (Exception, KeyboardInterrupt) as e:
        # remove unfinished sims
        clean_sims(simset_name)
        # reraise error
        raise e



if __name__ == "__main__":
    main()
