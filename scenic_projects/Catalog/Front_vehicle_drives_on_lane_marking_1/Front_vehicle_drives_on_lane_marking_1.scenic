# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On the ego's lane, a vehicle in front drives on left lane marking

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

import carla
import time

roadSec = network.elements['road8'].sections[0]
ego_car_type = 'vehicle.tesla.model3'
truck_type = 'vehicle.mercedes.sprinter'
target_type = 'vehicle.volkswagen.t2'

start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start

# Speed of vehicles
V1_speed = 11.11

# location of vehicles
road_length = 308.69
Ego_loc = 140
V1_loc = 170 - 14

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        ego = new Car following roadDirection from start_spot for Ego_loc, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero", \
            with behavior FollowLaneBehavior()

        
        # Front car V1
        v2 = new Car following roadDirection from start_spot for V1_loc, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "V1", \
            with behavior FollowLeftEdgeBehavior()
