import time
import os
import subprocess


# Expand the ~ character to the home directory
home_directory = os.path.expanduser('~')
subprocess.run(['tmux', 'kill-session', '-t', 'carla_session'])
command_list = [
    {'command': ['tmux', 'new-session', '-d', '-s', 'carla_session', 'bash', '-c', './CarlaUE4.sh'], 'cwd': os.path.join(home_directory, 'Tools/CARLA_0.9.13/')},
    {'command': "./docker/scripts/dev_start.sh", 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    # {'command': ['docker','exec','-u','weidong','apollo_dev_weidong','tail','/home/weidong/.bashrc'], 'cwd': home_directory},
    # {'command': "./docker/scripts/dev_into.sh", 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['git','checkout','--','modules/common/data/global_flagfile.txt'], 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['docker','exec','-u','weidong','apollo_dev_weidong','./scripts/bootstrap.sh'], 'cwd': home_directory},
    {'command': ['docker','exec','-w','/apollo/modules/carla_bridge/','-u','weidong','apollo_dev_weidong', 'sh', '-c','tail /home/weidong/.bashrc && python main.py'], 'cwd': home_directory},
    {'command': ['python3','./set_destination.py'], 'cwd': os.path.join(home_directory, "Tools/Scenic/scripts/")},
    # {'command': ['tmux', 'kill-session', '-t', 'carla_session'], 'cwd': home_directory}
]

# Run the command and capture the output
for command in command_list:
    print(f"Running command: {command['command']} in directory {command['cwd']}")
    result = subprocess.run(command['command'], cwd=command['cwd'])
    print(f"Command: {command['command']} returns code {result.returncode}. ")
    if result.returncode != 0:
        raise Exception(f"Command: {command['command']} failed. ")
    time.sleep(2)

# # Print the output and return code
# print("Output:", result.stdout)
# print("Error:", result.stderr)
# print("Return Code:", result.returncode)
