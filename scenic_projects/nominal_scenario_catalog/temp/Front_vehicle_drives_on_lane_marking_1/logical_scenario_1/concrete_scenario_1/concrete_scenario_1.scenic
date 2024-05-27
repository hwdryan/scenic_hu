# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On the opposite lane a cyclist drives following lane

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
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
cyclist_type = 'vehicle.bh.crossbike'

# Speed of vehicles
C1_speed = 11.11

# location of vehicles
road_length = 308.69
Ego_loc = 50
destination_loc = Ego_loc + 125
C1_loc = road_length - 100

behavior C1Behavoir(target_speed):
    try:
        wait
    interrupt when self.EgoInitControl():
        do FollowLaneBehavior(target_speed=target_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint target_vehicle_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior()

        # Cyclist C1
        end_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        cyslist_spot = new OrientedPoint following roadDirection from end_spot for C1_loc
        cyclist = new Bicycle at cyslist_spot,  \
                facing 0.1 deg relative to roadDirection, \
                with behavior C1Behavoir(target_speed=C1_speed), \
                with color Color(1,0,0), \
                with rolename "C1", \
                with blueprint cyclist_type
