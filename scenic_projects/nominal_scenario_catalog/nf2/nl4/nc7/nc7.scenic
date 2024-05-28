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

# long road
roadSec = network.elements['road6'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'

# Speed of vehicles
Mock_speed = 7

# location of vehicles
road_length = 224.22
Ego_loc = 40
destination_loc = Ego_loc + 125
Mock_loc = road_length - 120

scenario Main():
    setup:
        # Ego vehicle
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