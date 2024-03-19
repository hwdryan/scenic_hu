import time
import os
import subprocess


# Expand the ~ character to the home directory
home_directory = os.path.expanduser('~')
subprocess.run(['tmux', 'kill-session', '-t', 'carla_session'])
subprocess.run(['tmux', 'kill-session', '-t', 'bridge_session'])
subprocess.run(['tmux', 'kill-session', '-t', 'scenic_session'])
subprocess.run(['pkill','-f','CarlaUE4'])

command_list = [
    {'command': ['tmux', 'new-session', '-d', '-s', 'carla_session', 'bash', '-c', './CarlaUE4.sh'], 'cwd': os.path.join(home_directory, 'Tools/CARLA_0.9.13/')},
    {'command': ["./docker/scripts/dev_start.sh"], 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['git','checkout','--','modules/common/data/global_flagfile.txt'], 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['docker','exec','-u','weidonghu','apollo_dev_weidonghu','./scripts/bootstrap.sh'], 'cwd': home_directory},
    {'command': ['tmux', 'new-session', '-d', '-s', 'bridge_session', 
                 'docker','exec',
                 '-w','/apollo/modules/carla_bridge/',
                 '-u','weidonghu','apollo_dev_weidonghu', 
                 'sh', '-c',
                 'export PYTHONPATH=$PYTHONPATH:/apollo/bazel-bin/cyber/python/internal && \
                    export PYTHONPATH=$PYTHONPATH:/apollo/bazel-bin && \
                    export PYTHONPATH=$PYTHONPATH:/apollo/cyber && \
                    export PYTHONPATH=$PYTHONPATH:/apollo/cyber/python && \
                    export PYTHONPATH=$PYTHONPATH:/apollo && \
                    export PYTHONPATH=$PYTHONPATH:/apollo/modules && \
                    export PYTHONPATH=$PYTHONPATH:/apollo/modules/carla_bridge/carla_api/carla-0.9.13-py3.7-linux-x86_64.egg && \
                    echo $PYTHONPATH && \
                    python main.py'], 'cwd': home_directory, 'wait':5},
    {'command': ['tmux', 'new-session', '-d', '-s', 'scenic_session','conda','run','-n','scenic_related','python3','./Zhijing_scenario/store.py'], 'cwd': os.path.join(home_directory, "Tools/Scenic/scenic_projects/"), 'wait':10},
    {'command': ['python3','./set_destination.py'], 'cwd': os.path.join(home_directory, "Tools/Scenic/scripts/")},
    # {'command': ['tmux', 'kill-session', '-t', 'carla_session'], 'cwd': home_directory}
]

# Run the command and capture the output
for command in command_list:
    print(f"Running command: {' '.join(command['command'])} in directory {command['cwd']}")
    result = subprocess.run(command['command'], cwd=command['cwd'])
    print(f"Command: {' '.join(command['command'])} returns code {result.returncode}. ")
    if result.returncode != 0:
        raise Exception(f"Command: {' '.join(command['command'])} failed. ")
    if 'wait' in command:
        time.sleep(command['wait'])

# # Print the output and return code
# print("Output:", result.stdout)
# print("Error:", result.stderr)
# print("Return Code:", result.returncode)


