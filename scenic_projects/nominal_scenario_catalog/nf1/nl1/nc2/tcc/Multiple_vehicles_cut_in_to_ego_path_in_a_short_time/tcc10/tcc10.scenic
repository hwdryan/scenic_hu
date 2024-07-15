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

# long road
roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'

# Speed of vehicles
V1_speed = V2_speed = 12

# location of vehicles
road_length = 308.69
Ego_loc = 100
destination_loc = Ego_loc + 125
V1_loc = 1
V2_loc = 15
overtake_distance = -15

behavior VehicleLightBehavior():
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker))

behavior OvertakeBehavior(target_speed,avoidance_threshold=5):
    originalSec = self.laneSection
    laneToLeftSec = self.laneSection.laneToLeft
    try:
        wait
    interrupt when self.EgoInitControl():
        try:
            do LaneChangeBehavior(
                    laneSectionToSwitch=laneToLeftSec,
                    is_oppositeTraffic=True,
                    target_speed=(target_speed*0.9))
            do FollowLaneBehavior(
                    is_oppositeTraffic=True,
                    target_speed=target_speed)
        interrupt when self.longitudinaldistanceToEgo() <= overtake_distance:
            do LaneChangeBehavior(
                    laneSectionToSwitch=originalSec,
                    target_speed=target_speed)
            do FollowLaneBehavior(target_speed=target_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # overtake vehicle V1
        overtake_vehicle = new Car following roadDirection from start_spot for V1_loc,  \
                        facing 0.1 deg relative to roadDirection,
                        with color Color(0,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V1", \
                        with behavior OvertakeBehavior(target_speed=V1_speed)

        # overtake vehicle V2
        overtake_vehicle = new Car following roadDirection from start_spot for V2_loc,  \
                        facing 0.1 deg relative to roadDirection,
                        with color Color(1,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V2", \
                        with behavior OvertakeBehavior(target_speed=V2_speed)
