# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# Cyclist crosses from ego's roadside


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
ego_car_type = 'vehicle.tesla.model3'
cyclist_type = 'vehicle.bh.crossbike'
# Speed of vehicles
V1_speed = 11.11

# location of vehicles
road_length = 308.69
Ego_loc = 120

oppo_curb_middle = new OrientedPoint on roadSec.backwardLanes[0].group.curb.middle
brake_spot = new OrientedPoint right of oppo_curb_middle by 1.5
behavior CyclistCrossingBehavior(target_speed=10,avoidance_threshold=25):
    try:
        wait
    interrupt when self.distanceToEgo() <= avoidance_threshold:
        try:
            do ConstantSpeedBehavior(target_speed)
        interrupt when (distance from self to brake_spot) < 1:
            do BrakeBehavior()

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc +125
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior(target_speed=3)

        
        # Cyclist V1 
        curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle 
        cyclist_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection

        cyclist = new Bicycle left of cyclist_spot by 2, \
            facing 270 deg relative to roadDirection, \
            with color Color(1,0,0), \
            with behavior CyclistCrossingBehavior(), \
            with rolename "C1", \
            with blueprint cyclist_type

