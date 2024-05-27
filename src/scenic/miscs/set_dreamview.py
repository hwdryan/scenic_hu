import time
import json
from pprint import pprint
from websocket import create_connection
import os 
import math
import subprocess

def set_dreamview():
    # connect to dreamview
    ip = 'localhost'
    port = '8888'
    url = "ws://" + ip + ":" + port + "/websocket"
    ws = create_connection(url)

    # Set map
    hd_map = "carla_town01"
    word_list = []
    for s in hd_map.split('_'):
        word_list.append(s[0].upper() + s[1:])

    mapped_map = ' '.join(word_list)
    ws.send(json.dumps({"type": "HMIAction", "action": "CHANGE_MAP", "value": mapped_map}))

    # Set vehicle
    vehicle = "Lincoln2017MKZ_LGSVL"
    word_list = []
    for s in vehicle.split('_'):
        word_list.append(s[0].upper() + s[1:])

    mapped_vehicle = ' '.join(word_list)
    ws.send(json.dumps({"type": "HMIAction", "action": "CHANGE_VEHICLE", "value": mapped_vehicle}))

    # Open modules
    apollo_modules = [
        'Routing',
        'Prediction',
        'Planning',
        'Control',
    ]
    for apollo_module in apollo_modules:
        ws.send(json.dumps({"type": "HMIAction", "action": "START_MODULE", "value": apollo_module}))
    # Wait for all modules to be launched
    modules_launched = False
    while not modules_launched:
        modules_launched = True
        data = json.loads(ws.recv())
        while data["type"] != "HMIStatus":
            data = json.loads(ws.recv())
        print(data['data']['modules'])
        for apollo_module in apollo_modules:
            if not data['data']['modules'][apollo_module]:
                modules_launched = False
                break  # Break the loop if any apollo_module is False
    
    print("All modules launched.")
    # Wait
    time.sleep(5)

    # Set destination
    # Read the JSON file
    home_directory = os.path.expanduser('~')
    config_path = os.path.join(home_directory, "Tools/apollo/modules/carla_bridge/config/objects.json")
    with open(config_path, 'r') as file:
        data = json.load(file)
    
    x = data['objects'][1]['spawn_point']['x']
    y = data['objects'][1]['spawn_point']['y']
    z = data['objects'][1]['spawn_point']['z']
    d_x = data['objects'][1]['destination_point']['x']
    d_y = data['objects'][1]['destination_point']['y']
    d_z = data['objects'][1]['destination_point']['z']
    # heading = -1*math.radians(data['objects'][1]['spawn_point']['yaw'])
    heading = math.radians(data['objects'][1]['spawn_point']['yaw'] - data['objects'][1]['spawn_point']['roll'])
    msg = {
        "type": "SendRoutingRequest",
        "start": {    
            "x": x,
            "y": y,
            "z": z,
            "heading": heading,
        },
        "end": {"x": d_x, "y": d_y, "z": d_z},
        "waypoint": "[]",
    }
    ws.send(json.dumps(msg))
    
def close_modules():
    # 
    username = os.getlogin()
    subprocess.run(f"docker exec apollo_dev_{username} ps aux | grep 'python main.py' | grep -v grep | awk '{{print $2}}' | xargs docker exec apollo_dev_{username} kill -SIGINT", shell=True)
    subprocess.run(['tmux', 'kill-session', '-t', 'bridge_session'])# connect to dreamview
    # 
    try:
        ip = 'localhost'
        port = '8888'
        url = "ws://" + ip + ":" + port + "/websocket"
        ws = create_connection(url)

        # Open modules
        apollo_modules = [
            'Routing',
            'Prediction',
            'Planning',
            'Control',
        ]
        for apollo_module in apollo_modules:
            ws.send(json.dumps({"type": "HMIAction", "action": "STOP_MODULE", "value": apollo_module}))
    except ConnectionRefusedError:
        pass

def temp():
    ip = 'localhost'
    port = '8888'
    url = "ws://" + ip + ":" + port + "/websocket"
    ws = create_connection(url)


    msg = {'type': 'SendRoutingRequest', 
        'start': {'x': 396.33056640625, 'y': -268.5392150878906, 'z': 0.6000000238418579, 'heading': 1.5711848819979393}, 
        'end': {'x': 396.2988586425781, 'y': -143.53921508789062, 'z': 0.0}, 
        'waypoint': '[]'}

    ws.send(json.dumps(msg))
