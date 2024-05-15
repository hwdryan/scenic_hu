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

roadSec_west = network.elements['road6'].sections[0]
roadSec_east = network.elements['road7'].sections[0]
roadSec_north = network.elements['road19'].sections[0]
intersection_roadSec = network.elements['road157'].sections[0]
roadSec2 = network.elements['road5'].sections[0]
ego_car_type = 'vehicle.lincoln.mkz_2017'

# location of vehicles
road_west_length = 224.09
road_east_length = 36.35
road_north_length = 108.29
road_intersection_length = 22.01
Ego_loc = Range(160,200)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec_west.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.end
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
