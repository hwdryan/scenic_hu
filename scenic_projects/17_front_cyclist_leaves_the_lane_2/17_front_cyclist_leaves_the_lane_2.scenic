# Ego change lane to right, front cyclist also changes to the right

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'
crosswalk = network.elements['road934'].sections[0]


behavior CyclistBehavior(target_speed=10, change_time=8):
    do FollowLaneBehavior(target_speed=target_speed) for change_time seconds
    do LaneChangeBehavior(
            laneSectionToSwitch=self.laneSection.laneToRight,
            target_speed=target_speed)
    do FollowLaneBehavior(target_speed=target_speed)


behavior EgoBehavior(target_speed=10, change_time=8):
    do FollowLaneBehavior(target_speed=target_speed) for change_time seconds
    do LaneChangeBehavior(
            laneSectionToSwitch=self.laneSection.laneToRight,
            target_speed=target_speed)
    do FollowLaneBehavior(target_speed=target_speed)
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for 1
        print(f"Ego position: {ego_spot.pos_and_ori()}")

        # ego = new Car following roadDirection from start_spot for 1, \
        #     with behavior EgoBehavior(target_speed=3), \
        #     facing 0 deg relative to roadDirection, \
        #     with FollowLaneBehavior(), \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero"

        # front cyclist
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for 5
        cyclist = new Bicycle at cyslist_spot,  \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior CyclistBehavior()

        
