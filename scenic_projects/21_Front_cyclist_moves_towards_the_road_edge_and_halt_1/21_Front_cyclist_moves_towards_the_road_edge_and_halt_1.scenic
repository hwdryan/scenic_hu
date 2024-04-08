# 1. Front cyclist moves towards the road edge to talk with a pedestrian

param map = localPath("../../assets/maps/CARLA/Town04.xodr")
param carla_map = 'Town04'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road29'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'


behavior CyclistBehavior(target_speed=10,avoidance_threshold=18):
    try:
        do FollowLaneBehavior(target_speed=target_speed)
    interrupt when self.distanceToClosest(_model.Pedestrian) <= avoidance_threshold:
        shoulder_laneSce = self.laneSection
        # shoulder_lane = self.laneSection.group.shoulder
        nearby_intersection = self.laneSection.group._shoulder.centerline[-1]
        try:
            do FollowRightEdgeBehavior(target_speed=target_speed)
        interrupt when self.distanceToClosest(_model.Pedestrian) <= 3:
            do BreakBehavior()

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
        ego_spot = new OrientedPoint following roadDirection from start_spot for 1
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        
        # ego = new Car following roadDirection from start_spot for 1, \
        #     with behavior FollowLaneBehavior(target_speed=3), \
        #     facing 0 deg relative to roadDirection, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero"
    
        # front cyclist
        lane = ego.laneGroup.lanes[0]
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for 5
        cyclist = new Bicycle at cyslist_spot,  \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior CyclistBehavior()

        # pedestrian
        sidewalk_middle = new OrientedPoint on roadSec.road.laneGroups[0].sidewalk.centerline.middle
        ped_spot = new OrientedPoint on sidewalk_middle, facing 180 deg relative to roadDirection
        ped = new Pedestrian right of ped_spot by 0.1
        

