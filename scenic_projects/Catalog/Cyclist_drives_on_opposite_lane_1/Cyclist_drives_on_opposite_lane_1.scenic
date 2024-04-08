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
ego_car_type = 'vehicle.tesla.model3'
truck_type = 'vehicle.mercedes.sprinter'
target_type = 'vehicle.volkswagen.t2'

start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start

# Speed of vehicles
V1_speed = 11.11

# location of vehicles
road_length = 308.69
Ego_loc = 50
V1_loc = road_length - 100

behavior V1Behavior():
    try:
        wait
    interrupt when self.SpeedOfEgo() > 0.01:
        do FollowLaneBehavior(target_speed=V1_speed)

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

        # cyclist
        end_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        cyslist_spot = new OrientedPoint following roadDirection from end_spot for V1_loc
        cyclist = new Bicycle at cyslist_spot,  \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior FollowLaneBehavior(target_speed=V1_speed), \
                        with rolename "V1"
