################
# Scenic code
################
param map = localPath("../../assets/maps/CARLA/Town04.xodr")
param carla_map = 'Town04'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

road = random.choice(['road8','road15'])
roadSec = network.elements[road].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
cyclist_type = 'vehicle.bh.crossbike'

# Speed of vehicles
C1_speed = Range(1,3)

# location of vehicles
road_length = 308.69
Ego_loc = Range(1,road_length-125)
destination_loc = Ego_loc + 125
C1_loc = Range(Ego_loc, Ego_loc+110)

# Time for meneuvor
C1_duration = Range(3,5)

behavior CyclistBehavior(target_speed,avoidance_threshold=18):
    try:
        wait
    interrupt when self.EgoInitControl():
        do FollowRightEdgeBehavior(target_speed=target_speed) for C1_duration seconds
        do BrakeBehavior()
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # Cyclist C1
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for C1_loc
        cyclist = new Bicycle at cyslist_spot,  \
                facing 0.1 deg relative to roadDirection, \
                with behavior CyclistBehavior(target_speed=C1_speed), \
                with color Color(1,0,0), \
                with rolename "C1", \
                with blueprint cyclist_type

