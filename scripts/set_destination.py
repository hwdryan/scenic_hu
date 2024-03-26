import time
import json
from pprint import pprint
from websocket import create_connection

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
modules = [
    'Routing',
    'Prediction',
    'Planning',
    'Control',
]
for module in modules:
    ws.send(json.dumps({"type": "HMIAction", "action": "START_MODULE", "value": module}))
# Wait for all modules to be launched
modules_launched = False
while not modules_launched:
    data = json.loads(ws.recv())
    while data["type"] != "HMIStatus":
        data = json.loads(ws.recv())
    for module in modules:
        if not data['data']['modules'][module]:
            modules_launched = False
            break  # Break the loop if any module is False
        modules_launched = True
# Wait
time.sleep(5)

# Set destination
msg = {
    "type": "SendRoutingRequest",
    "start": {    
        "x": 396.33447265625,
        "y": -278.5392150878906,
        "z": 0.6000000238418579,
        "heading": 1.5711844825237757,
    },
    "end": {"x": 396.30413818359375, "y": -18.53921508789062, "z": 0},
    "waypoint": "[]",
}

ws.send(json.dumps(msg))


    