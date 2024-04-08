# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# ego follows lane, while multiple vehicle cut in to ego path in short time



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
V1_speed = 12
V3_speed = 5

# location of vehicles
road_length = 308.69
Ego_loc = 35
V1_loc = 1
V2_loc = 15

# self-defined
behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

behavior OvertakeBehavior(target_speed=V1_speed,avoidance_threshold=20, bypass_dist=17):
    originalSec = self.laneSection
    laneToLeftSec = self.laneSection.laneToLeft
    try:
        do LaneChangeBehavior(
                laneSectionToSwitch=laneToLeftSec,
                is_oppositeTraffic=True,
                target_speed=target_speed)
        do FollowLaneBehavior(
                is_oppositeTraffic=True,
                target_speed=target_speed)
    interrupt when self.distanceToEgo() <= 5:
        do LaneChangeBehavior(
                laneSectionToSwitch=originalSec,
                target_speed=target_speed)
        do FollowLaneBehavior(target_speed=target_speed)

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
            with behavior FollowLaneBehavior(target_speed=7)

        # overtake vehicle V1
        overtake_vehicle = new Car following roadDirection from start_spot for V1_loc,  \
                        with color Color(0,0,1), \
                        with blueprint target_type, \
                        with rolename "V1", \
                        with behavior OvertakeBehavior()

        # overtake vehicle V2
        overtake_vehicle = new Car following roadDirection from start_spot for V2_loc,  \
                        with color Color(1,0,1), \
                        with blueprint target_type, \
                        with rolename "V2", \
                        with behavior OvertakeBehavior()
