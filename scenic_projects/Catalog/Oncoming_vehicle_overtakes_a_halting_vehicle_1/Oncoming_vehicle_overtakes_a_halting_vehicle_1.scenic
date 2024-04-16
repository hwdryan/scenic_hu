# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On the opposite lane a delivery vehicle halts with warning flasher. The vehicle behind it performs overtaking via ego's lane.



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
V1_speed = 11.11
V3_speed = 5

# location of vehicles
road_length = 308.69
Ego_loc = 140
V1_loc = 170 - 14

V2_loc = road_length - 180
V3_loc = road_length - 210 - 5.5

# self-defined
behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

behavior OvertakeBehavior(target_speed=V3_speed,avoidance_threshold=20, bypass_dist=17):
    changeback_spot = new OrientedPoint following roadDirection from start_spot for (road_length - V2_loc)
    try:
        wait
    interrupt when self.SpeedOfEgo() > 0.01:
        try:
            do FollowLaneBehavior(target_speed=target_speed)
        interrupt when self.distanceToClosest(Truck) < bypass_dist:
            originalSec = self.laneSection
            laneToLeftSec = self.laneSection.laneToLeft
            try:
                do LaneChangeBehavior(
                        laneSectionToSwitch=laneToLeftSec,
                        is_oppositeTraffic=True,
                        target_speed=target_speed)
            interrupt when (distance from self to changeback_spot) < 2:
                do LaneChangeBehavior(
                        laneSectionToSwitch=originalSec,
                        target_speed=target_speed)
                do FollowLaneBehavior(target_speed=target_speed)
    
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
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc + 125
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior()

        
        # Front car V1
        v2 = new Car following roadDirection from start_spot for V1_loc, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "V1", \
            with behavior V1Behavior()
            
        # halting vehicle with warning flasher V2
        parked_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        parked_vehicle = new Truck following roadDirection from parked_vehicle_spot for V2_loc,  \
                        with color Color(0,1,0), \
                        with blueprint truck_type, \
                        with behavior VehicleLightBehavior(), \
                        with rolename "V2"

        # overtake vehicle V3
        overtake_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        overtake_vehicle = new Car following roadDirection from overtake_vehicle_spot for V3_loc,  \
                        with color Color(0,0,1), \
                        with blueprint target_type, \
                        with rolename "V3", \
                        with behavior OvertakeBehavior()
