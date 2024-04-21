command_list = [
    {'command': ['./CarlaUE4.sh'], 'cwd': os.path.join(home_directory, 'Tools/CARLA_0.9.15/'), 'close_fds':True},
    {'command': ["./docker/scripts/dev_start.sh"], 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    # {'command': ['docker','exec','-u','weidonghu','apollo_dev_weidonghu','tail','/home/weidonghu/.bashrc'], 'cwd': home_directory},
    # {'command': "./docker/scripts/dev_into.sh", 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['git','checkout','--','modules/common/data/global_flagfile.txt'], 'cwd': os.path.join(home_directory, "Tools/apollo/")},
    {'command': ['docker','exec','-u','weidonghu','apollo_dev_weidonghu','./scripts/bootstrap.sh'], 'cwd': home_directory},
    {'command': ['docker','exec','-w','/apollo/modules/carla_bridge/','-u','weidonghu','apollo_dev_weidonghu', 'sh', '-c','source /home/weidonghu/.bashrc && tail /home/weidonghu/.bashrc && echo $PYTHONPATH && python main.py'], 'cwd': home_directory, 'close_fds':True},
    {'command': ['python3','./set_destination.py'], 'cwd': os.path.join(home_directory, "Tools/Scenic/scripts/")},
    # {'command': ['tmux', 'kill-session', '-t', 'carla_session'], 'cwd': home_directory}
]


DOCKER_USER="${USER}"
DEV_CONTAINER="apollo_dev_${USER}"

# Launch Carla
cd "$CARLA_ROOT"
bash ./CarlaUE4.sh &

sleep 5

# Start apollo container
cd "$APOLLO_ROOT"
bash ./docker/scripts/dev_start.sh

Checkout flagfile
git checkout -- modules/common/data/global_flagfile.txt

# # Launch dreamview
# docker exec \
#     -u "${DOCKER_USER}" \
#     "${DEV_CONTAINER}" \
#     ./scripts/bootstrap.sh

export PYTHONPATH=$PYTHONPATH:/apollo/cyber && export PYTHONPATH=$PYTHONPATH:/apollo/cyber/python && export PYTHONPATH=$PYTHONPATH:/apollo && export PYTHONPATH=$PYTHONPATH:/apollo/modules && export PYTHONPATH=$PYTHONPATH:/apollo/modules/carla_bridge/carla_api/carla-0.9.15-py3.7-linux-x86_64.egg