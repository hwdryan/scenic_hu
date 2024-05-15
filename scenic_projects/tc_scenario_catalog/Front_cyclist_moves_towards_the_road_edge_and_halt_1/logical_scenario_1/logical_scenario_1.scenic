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
ego_car_type = 'vehicle.volkswagen.t2'
cyclist_type = 'vehicle.diamondback.century'
pedestrian_type = 'walker.pedestrian.0006'

# Speed of vehicles
C1_speed = Range(1, 11.11)

# location of vehicles
road_length = 308.69
Ego_loc = Range(1,100)
C1_loc = Range(Ego_loc + 3,110)
destination_loc = Ego_loc + 125

behavior CyclistBehavior(target_speed,avoidance_threshold=18):
    try:
        wait
    interrupt when self.EgoInitControl():
        try:
            do FollowLaneBehavior(target_speed=target_speed)
        interrupt when self.distanceToClosest(_model.Pedestrian) <= avoidance_threshold:
            shoulder_laneSce = self.laneSection
            # shoulder_lane = self.laneSection.group.shoulder
            nearby_intersection = self.laneSection.group._shoulder.centerline[-1]
            try:
                do FollowRightEdgeBehavior(target_speed=target_speed)
            interrupt when self.distanceToClosest(_model.Pedestrian) <= 3:
                do BrakeBehavior()

            # do LaneChangeToShoulderBehavior(
            #         laneSectionToSwitch=shoulder_laneSce,
            #         target_speed=target_speed)
            # do FollowShoulderBehavior(
            #         target_speed=target_speed,
            #         laneToFollow=shoulder_lane)
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for destination_loc
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")
        
        # ego = new Car following roadDirection from start_spot for 1, \
        #     with behavior FollowLaneBehavior(target_speed=4), \
        #     facing 0 deg relative to roadDirection, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero"

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
        

