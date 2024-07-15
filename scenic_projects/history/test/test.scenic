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

# long road
roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'

# Speed of vehicles
V1_speed = V2_speed = V3_speed = 12

# location of vehicles
road_length = 308.69
Ego_loc = 50
destination_loc = Ego_loc + 125
V1_loc = 1
V2_loc = 15
V3_loc = 30
overtake_distance = -15

behavior VehicleLightBehavior():
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker))

behavior OvertakeBehavior(target_speed,avoidance_threshold=5):
    originalSec = self.laneSection
    laneToLeftSec = self.laneSection.laneToLeft
    try:
        wait
    # interrupt when self.EgoInitControl():
    interrupt when True:
        try:
            do FollowLaneBehavior(
                    is_oppositeTraffic=True,
                    target_speed=target_speed)
        interrupt when self.longitudinaldistanceToEgo() <= overtake_distance:
            do LaneChangeBehavior(
                    laneSectionToSwitch=laneToLeftSec,
                    target_speed=target_speed)
            do FollowLaneBehavior(target_speed=target_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        dummy_start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start

        dummy = new Car following roadDirection from dummy_start_spot for Ego_loc, \
            facing 0.01 deg relative to roadDirection, \
            with blueprint target_vehicle_type, \
            with color Color(1,0,0), \
            with rolename "hero", \
            with behavior DriveAvoidingCollisions(target_speed=0.45, avoidance_threshold = 6)

        
        overtake_start_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start

        # overtake vehicle V1
        ego = new Car following roadDirection from overtake_start_spot for road_length - V1_loc,  \
                        facing 180 deg relative to roadDirection,
                        with color Color(0,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V1", \
                        with behavior BrakeBehavior()

        # overtake vehicle V2
        overtake_vehicle = new Car following roadDirection from overtake_start_spot for road_length - V2_loc,  \
                        facing 180 deg relative to roadDirection,
                        with color Color(1,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V2", \
                        with behavior OvertakeBehavior(target_speed=V2_speed)

        # overtake vehicle V3
        overtake_vehicle = new Car following roadDirection from overtake_start_spot for road_length - V3_loc,  \
                        facing 180 deg relative to roadDirection,
                        with color Color(1,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V3", \
                        with behavior OvertakeBehavior(target_speed=V3_speed)
