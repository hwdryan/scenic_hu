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

roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.volkswagen.t2'
truck_type = 'vehicle.mercedes.sprinter'

start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start

# Speed of vehicles
V2_speed = 5

# location of vehicles
road_length = 308.69
Ego_loc = 50

V1_loc = road_length - 120
V2_loc = road_length - 170

behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

behavior OvertakeBehavior(target_speed=V2_speed, bypass_dist=17):
    changeback_spot = new OrientedPoint following roadDirection from start_spot for (road_length - V1_loc)
    try:
        wait
    interrupt when self.EgoInitControl():
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

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc + 125
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
            
        # halting vehicle with warning flasher V1
        parked_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        parked_vehicle = new Truck following roadDirection from parked_vehicle_spot for V1_loc,  \
                        with color Color(0,1,0), \
                        with blueprint truck_type, \
                        with behavior VehicleLightBehavior(), \
                        with rolename "V1"

        # overtake vehicle V2
        overtake_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        overtake_vehicle = new Car following roadDirection from overtake_vehicle_spot for V2_loc,  \
                        with color Color(0,0,1), \
                        with blueprint target_vehicle_type, \
                        with rolename "V2", \
                        with behavior OvertakeBehavior()
