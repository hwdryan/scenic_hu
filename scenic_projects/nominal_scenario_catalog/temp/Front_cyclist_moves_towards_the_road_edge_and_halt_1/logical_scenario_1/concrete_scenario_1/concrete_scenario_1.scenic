# 1. One a straight road, Front cyclist moves towards the road edge to talk with a pedestrian


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
target_vehicle_type = 'vehicle.volkswagen.t2'
cyclist_type = 'vehicle.diamondback.century'
pedestrian_type = 'walker.pedestrian.0006'

# Speed of vehicles
C1_speed = 5.5

# location of vehicles
road_length = 308.69
Ego_loc = 75
C1_loc = 90

behavior CyclistBehavior(target_speed,avoidance_threshold=18):
    try:
        wait
    interrupt when self.EgoInitControl():
        try:
            do FollowLaneBehavior(target_speed=target_speed)
        interrupt when self.distanceToClosest(_model.Pedestrian) <= avoidance_threshold:
            
            try:
                do FollowRightEdgeBehavior(target_speed=target_speed)
            interrupt when self.distanceToClosest(_model.Pedestrian) <= 3:
                do BrakeBehavior()

            
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc + 125
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

        # pedestrian
        sidewalk_middle = new OrientedPoint on roadSec.road.laneGroups[0].sidewalk.centerline.middle
        ped_spot = new OrientedPoint on sidewalk_middle, facing 270 deg relative to roadDirection
        ped = new Pedestrian left of ped_spot by 0.3, \
                with rolename "P1", \
                with blueprint pedestrian_type
        

