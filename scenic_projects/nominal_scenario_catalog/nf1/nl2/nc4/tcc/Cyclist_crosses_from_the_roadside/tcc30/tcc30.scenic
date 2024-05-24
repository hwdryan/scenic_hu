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

roadSec = network.elements['road6'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
cyclist_type = 'vehicle.bh.crossbike'
# Speed of vehicles
C1_speed = 4.16

# location of vehicles
road_length = 224.22
Ego_loc = 80
destination_loc = Ego_loc + 125
distance_threshold = 25


oppo_curb_middle = new OrientedPoint on roadSec.backwardLanes[0].group.curb.middle
brake_spot = new OrientedPoint right of oppo_curb_middle by 1.5
behavior CyclistCrossingBehavior(target_speed=C1_speed,distance_threshold=distance_threshold):
    try:
        wait
    interrupt when self.distanceToEgo() <= distance_threshold:
        try:
            do ConstantSpeedBehavior(target_speed)
        interrupt when (distance from self to brake_spot) < 1:
            do BrakeBehavior()

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        
        # Cyclist C1 
        curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle 
        cyclist_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection

        cyclist = new Bicycle left of cyclist_spot by 2, \
            facing 270 deg relative to roadDirection, \
            with color Color(1,0,0), \
            with behavior CyclistCrossingBehavior(), \
            with rolename "C1", \
            with blueprint cyclist_type

