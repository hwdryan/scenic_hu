# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# Pedestrian halts sharply in front of the road edge


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
pedestrian_type = "walker.pedestrian.0001"

# Speed of vehicles
P1_speed = 11.11

# location of vehicles
road_length = 308.69
Ego_loc = 120

curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle
brake_spot = new OrientedPoint right of curb_middle by 1.5

behavior PedestrianHaltBehavior(target_speed=10,avoidance_threshold=20):
    try:
        wait
    interrupt when self.distanceToEgo() <= avoidance_threshold:
        try:
            do WalkwithDirectionBehavior(direction=270 deg relative to brake_spot.heading, speed = 4)
        interrupt when (distance from self to brake_spot) <= 1.8:
            do WalkwithDirectionBehavior(direction=90 deg relative to brake_spot.heading, speed = 0)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc + 125
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior(target_speed=3)

        
        # Pedestrian V1 
        curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle 
        ped_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection

        ped = new Pedestrian left of ped_spot by 2, \
            facing 270 deg relative to roadDirection, \
            with blueprint pedestrian_type, \
            with color Color(1,0,0), \
            with behavior PedestrianHaltBehavior()
