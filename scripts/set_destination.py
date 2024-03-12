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
# modules_launched = False
# while not modules_launched:
#     try:
#         states = json.loads(ws.recv())
#         for module in modules:
#             if not states['data']['modules'][module]:
#                 modules_launched = False
#                 break  # Break the loop if any module is False
#             modules_launched = True
#     except KeyError:
#         pass

# Wait
time.sleep(10)

# Set destination
msg = {
    "type": "SendRoutingRequest",
    "start": {    
        "x": 396.30413818359375,
        "y": -168.53921508789062,
        "z": 0.03354499861598015,
        "heading": 1.5710071159951764,
    },
    "end": {"x": 396.30413818359375, "y": -68.53921508789062, "z": 0},
    "waypoint": "[]",
}

ws.send(json.dumps(msg))




    