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
Mock_speed = 10
C1_speed = 2

# location of vehicles
road_length = 224.22
Ego_loc = 80
destination_loc = Ego_loc + 125
Mock_loc = road_length - 140
distance_threshold = 80/C1_speed

oppo_curb_middle = new OrientedPoint on roadSec.backwardLanes[0].group.curb.middle
brake_spot = new OrientedPoint ahead of oppo_curb_middle by 1.5
behavior CyclistCrossingBehavior(target_speed=C1_speed,distance_threshold=distance_threshold):
    try:
        wait
    interrupt when (self.EgolongitudinaldistanceToActor() <= distance_threshold) and (self.lateraldistanceToActor("Mock")>0):
        try:
            do ConstantSpeedBehavior(target_speed)
        interrupt when (distance from self to brake_spot) < 1:
            do BrakeBehavior()

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # Mock vehicle
        mock_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        mock_vehicle = new Car following roadDirection from mock_spot for Mock_loc,  \
                        with color Color(0,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "Mock", \
                        with behavior MockBehavior(target_speed=Mock_speed)

        # Cyclist C1 
        curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle 
        cyclist_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection
        cyclist = new Bicycle behind curb_middle by 1, \
            facing 0.01 deg relative to roadDirection, \
            with color Color(1,0,0), \
            with behavior CyclistCrossingBehavior(), \
            with rolename "C1", \
            with blueprint cyclist_type

