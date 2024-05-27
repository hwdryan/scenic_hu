# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On ego's lane, a delivery vehicle halts with warning flasher on.


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
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
truck_type = 'vehicle.mercedes.sprinter'

start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start

# location of vehicles
road_length = 308.69
Ego_loc = 100
V1_loc = 165

# self-defined
behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc, facing 0.01 deg relative to roadDirection
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc + 125
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        
        # ego = new Car following roadDirection from start_spot for Ego_loc, \
        #     with blueprint target_vehicle_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero", \
        #     with behavior FollowLaneBehavior()

        # Front halting vehicle with warning flasher V1
        parked_vehicle = new Truck following roadDirection from start_spot for V1_loc,  \
                        with color Color(0,1,0), \
                        with blueprint truck_type, \
                        with behavior VehicleLightBehavior(), \
                        with rolename "V1"

