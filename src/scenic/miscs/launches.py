###############
# Launch CARLA
###############
import subprocess
import os
import time
import docker
import json
from .set_dreamview import close_modules

username = os.getlogin()

def launch_carla():
    home_directory = os.path.expanduser('~')
    subprocess.run(['tmux', 'kill-session', '-t', 'carla_session'])
    subprocess.run(['tmux', 'kill-session', '-t', 'bridge_session'])
    subprocess.run(['pkill','-f','CarlaUE4'])
    subprocess.run(['tmux', 'new-session', '-d', '-s', 'carla_session', 'bash', '-c', './CarlaUE4.sh'], cwd = os.path.join(home_directory, 'Tools/CARLA_0.9.15/'))
    if not is_container_running("apollo_dev_"+os.getlogin()):
        subprocess.run(['./docker/scripts/dev_start.sh'], cwd = os.path.join(home_directory, "Tools/apollo/"))
    else:
        time.sleep(6)
        # kill bridge script
        subprocess.run(f"docker restart apollo_dev_{username}", shell=True)
        subprocess.run(f"docker exec apollo_dev_{username} ps aux | grep 'python main.py' | grep -v grep | awk '{{print $2}}' | xargs docker exec apollo_dev_{username} kill -SIGINT", shell=True)
        subprocess.run(['tmux', 'kill-session', '-t', 'bridge_session'])


def is_container_running(container_name):
    # Connect to the Docker daemon
    client = docker.from_env()

    try:
        # Get container object
        container = client.containers.get(container_name)
        # Check if container is running
        return container.status == "running"
    except docker.errors.NotFound:
        # Container does not exist
        return False

def launch_tools():
    # Launch Carla, Apollo, bridge
    home_directory = os.path.expanduser('~')
    close_modules()
    command_list = [
        {'command': ['git','checkout','--','modules/common/data/global_flagfile.txt'], 'cwd': os.path.join(home_directory, "Tools/apollo/"), 'print':True},
        {'command': ['docker','exec','-u',username,f'apollo_dev_{username}','./scripts/bootstrap.sh','restart'], 'cwd': home_directory},
        {'command': ['tmux', 'new-session', '-d', '-s', 'bridge_session', 
                    'docker','exec',
                    '-w','/apollo/modules/carla_bridge/',
                    '-u',username,f'apollo_dev_{username}', 
                    'sh', '-c',
                    'export PYTHONPATH=$PYTHONPATH:/apollo/bazel-bin/cyber/python/internal && \
                        export PYTHONPATH=$PYTHONPATH:/apollo/bazel-bin && \
                        export PYTHONPATH=$PYTHONPATH:/apollo/cyber && \
                        export PYTHONPATH=$PYTHONPATH:/apollo/cyber/python && \
                        export PYTHONPATH=$PYTHONPATH:/apollo && \
                        export PYTHONPATH=$PYTHONPATH:/apollo/modules && \
                        export PYTHONPATH=$PYTHONPATH:/apollo/modules/carla_bridge/carla_api/carla-0.9.15-py3.7-linux-x86_64.egg && \
                        echo $PYTHONPATH && \
                        python main.py'], 'cwd': home_directory, 'wait':5},
    ]

    # Run the command and capture the output
    for command in command_list:
        print(f"Running command: {' '.join(command['command'])} in directory {command['cwd']}")
        result_subprocess = subprocess.Popen(command['command'], cwd=command['cwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Read output and errors
        stdout, stderr = result_subprocess.communicate()
        # print("stdout:",stdout.decode())
        # print("stderr:",stderr.decode())
        return_code = result_subprocess.returncode
        if return_code == 0:
            print("Subprocess executed successfully")
        else:
            print(f"Subprocess failed with return code {return_code}")
        if 'wait' in command:
            print(f"wait for {command['wait']} seconds")
            time.sleep(command['wait'])

def change_spawn_point(x,y,z,pitch,yaw,roll):

    # Read the JSON file
    home_directory = os.path.expanduser('~')
    config_path = os.path.join(home_directory, "Tools/apollo/modules/carla_bridge/config/objects.json")
    with open(config_path, 'r') as file:
        data = json.load(file)

    # Modify the spawn point value
    data['objects'][1]['spawn_point']['x'] = float(x)
    data['objects'][1]['spawn_point']['y'] = float(y)
    data['objects'][1]['spawn_point']['z'] = float(z)
    data['objects'][1]['spawn_point']['pitch'] = float(pitch)
    data['objects'][1]['spawn_point']['yaw'] = float(yaw)
    data['objects'][1]['spawn_point']['roll'] = float(roll)

    # Write the updated JSON content back to the file
    with open(config_path, 'w') as file:
        json.dump(data, file, indent=4)

def change_destination_point(x,y,z):

    # Read the JSON file
    home_directory = os.path.expanduser('~')
    config_path = os.path.join(home_directory, "Tools/apollo/modules/carla_bridge/config/objects.json")
    with open(config_path, 'r') as file:
        data = json.load(file)

    # Modify the spawn point value
    data['objects'][1]['destination_point']['x'] = float(x)
    data['objects'][1]['destination_point']['y'] = float(y)
    data['objects'][1]['destination_point']['z'] = float(z)

    # Write the updated JSON content back to the file
    with open(config_path, 'w') as file:
        json.dump(data, file, indent=4)

