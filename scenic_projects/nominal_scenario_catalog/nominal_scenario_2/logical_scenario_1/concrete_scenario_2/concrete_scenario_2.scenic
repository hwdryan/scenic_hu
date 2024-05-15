################
# Scenic code
################
param map = localPath("../../assets/maps/CARLA/Town01.xodr")
param carla_map = 'Town01'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads
import scenic.simulators.carla.utils.utils as _utils
import scenic.simulators.carla.misc as _misc

import random
import carla
import time

roadSec = network.elements['road15'].sections[0]
corner_roadSec = network.elements['road20'].sections[0]
roadSec2 = network.elements['road5'].sections[0]
ego_car_type = 'vehicle.lincoln.mkz_2017'

# location of vehicles
road_length_1 = 308.69
road_length_corner = 16.70
road_length_2 = 69.62
Ego_loc = 250

scenario Main():
    setup:
        # Ego vehicle
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint on roadSec2.forwardLanes[0].centerline.middle
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")



