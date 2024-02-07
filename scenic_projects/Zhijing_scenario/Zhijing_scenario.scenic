# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On the opposite lane a delivery vehicle halts with warning flasher. The vehicle behind it performs overtaking via ego's lane.
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
Ego_speed = 5
V1_speed = 5
V2_speed = 5

# location of vehicles
road_length = 308.69
Ego_loc = 20
V1_loc = road_length - 90
V2_loc = 75
V3_loc = road_length - 70

# self-defined
behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

behavior OvertakeBehavior(target_speed=V1_speed,avoidance_threshold=25, bypass_dist=17):
    changeback_spot = new OrientedPoint following roadDirection from start_spot for 70
    try:
        wait
    interrupt when self.SpeedOfEgo() > 5:
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
            interrupt when (distance from self to changeback_spot) < 1.5:
                do LaneChangeBehavior(
                        laneSectionToSwitch=originalSec,
                        target_speed=target_speed)
                do FollowLaneBehavior(target_speed=target_speed)
    
behavior V2Behavior():
    try:
        wait
    interrupt when self.SpeedOfEgo() > 5:
        do FollowLaneBehavior(target_speed=V2_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        x = ego_spot.pos_and_ori().location.x
        y = ego_spot.pos_and_ori().location.y
        z = ego_spot.pos_and_ori().location.z
        pitch = ego_spot.pos_and_ori().rotation.pitch
        yaw = ego_spot.pos_and_ori().rotation.yaw
        roll = ego_spot.pos_and_ori().rotation.roll
        
        print(f"Ego position: {x},{y},{z},{pitch},{yaw},{roll}")
        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior()
        
        # Front car V2
        v2 = new Car following roadDirection from start_spot for V2_loc, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "v2", \
            with behavior V2Behavior()

        # halting vehicle with warning flasher V3
        parked_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        parked_vehicle = new Truck following roadDirection from parked_vehicle_spot for V3_loc,  \
                        with blueprint truck_type, \
                        with behavior VehicleLightBehavior(), \
                        with rolename "V3"

        # overtake vehicle V1
        overtake_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        overtake_vehicle = new Car following roadDirection from overtake_vehicle_spot for V1_loc,  \
                        with blueprint target_type, \
                        with rolename "V1", \
                        with behavior OvertakeBehavior()
