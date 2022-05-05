import argparse
import subprocess
from datetime import datetime
import os
import random

from analyze_logs import analyze_logs

parser = argparse.ArgumentParser()
parser.add_argument("--n-games",type=int,default=100)
parser.add_argument("--n-agents",type=int,default=15)
ARGS = parser.parse_args()


sim_name = "sim_{}".format(datetime.now().isoformat())

os.makedirs(f"sims/{sim_name}", exist_ok=True)


all_agents = {
    "SampleJava": "java,org.aiwolf.sample.player.SampleRoleAssignPlayer",
    "SamplePy": "python,sample-python-agent/start.py",
    "HALU": "python,other_agents/HALU/HALUemon.py",
    "OKAMI": "python,other_agents/OKAMI/OKAMI.py",
    "Takeda": "java,org.aiwolf.takeda.TakedaRoleAssignPlayer",
    "TOKU": "java,org.aiwolf.TOKU.TOKURoleAssginPlayer",
    "Tomato": "java,com.gmail.toooo1718tyan.Player.RoleAssignPlayer",
}

# choose n agents
selected_agents = random.choices(list(all_agents.keys()), k=ARGS.n_agents)
# format them
selected_agents = [f"{name}{i},{all_agents[name]}" for i,name in enumerate(selected_agents)]
selected_agents_str = "\n".join(selected_agents)

# config file contents
config = f"""
lib=./AIWolf-ver0.6.3/
log=./sims/{sim_name}/logs/
port=10000
game={ARGS.n_games}
view=false
#C#=PATH_TO_C#_CLIENT_STARTER
setting=./AIWolf-ver0.6.3/SampleSetting.cfg
#agent=5

{selected_agents_str}
"""

config_filename = f"sims/{sim_name}/config.ini"
with open(config_filename, "w") as f:
    f.write(config)

# classpath elements
classpath_list = [
    # server files
    "AIWolf-ver0.6.3/aiwolf-server.jar",
    "AIWolf-ver0.6.3/aiwolf-common.jar",
    "AIWolf-ver0.6.3/aiwolf-client.jar",
    "AIWolf-ver0.6.3/aiwolf-viewer.jar",
    "AIWolf-ver0.6.3/jsonic-1.3.10.jar",
    # agent jars (all are included regardless of it they are used, since it doesn't hurt)
    "other_agents/TakedaAgent/takedaAgent.jar",
    "other_agents/TeamSashimi/SashimiAgent.jar",
    "other_agents/TeamTomato/TomatoAgent.jar",
    "other_agents/TOKU/bin",
]

classpath = ":".join(classpath_list)
command = f"java -cp {classpath} org.aiwolf.ui.bin.AutoStarter {config_filename}"

subprocess.run(command, shell=True)

analyze_logs(f"sims/{sim_name}/logs/")