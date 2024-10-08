################
# Scenic code
################
param map = localPath("../../assets/maps/CARLA/Town04.xodr")
param carla_map = 'Town04'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
cyclist_type = 'vehicle.bh.crossbike'

# Speed of vehicles
C1_speed = 7
Mock_speed = 7

# location of vehicles
road_length = 308.69
Ego_loc = 50
destination_loc = Ego_loc + 125
Mock_loc = road_length - 150
C1_loc = 70

behavior CyclistBehavior(target_speed):
    try:
        wait
    interrupt when self.EgoInitControl():
        do ReachRightEdgeBehavior(target_speed=target_speed)
        
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
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for C1_loc
        cyclist = new Bicycle at cyslist_spot,  \
                facing 0.1 deg relative to roadDirection, \
                with behavior CyclistBehavior(target_speed=C1_speed), \
                with color Color(1,0,0), \
                with rolename "C1", \
                with blueprint cyclist_type

