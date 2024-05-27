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

roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'

# Speed of vehicles
V1_speed = Range(7,11.11)

# location of vehicles
road_length = 308.69
Ego_loc = Range(1,road_length-125)
destination_loc = Ego_loc + 125
V1_loc = Range(Ego_loc, road_length)

behavior V1Behavior(target_speed):
    try:
        wait
    interrupt when self.EgoInitControl():
        do FollowLeftEdgeBehavior(target_speed=target_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        
        # Front car V1
        v1 = new Car following roadDirection from start_spot for V1_loc, \
            with blueprint target_vehicle_type, \
            with color Color(1,0,0), \
            with rolename "V1", \
            with behavior V1Behavior(target_speed=V1_speed)
