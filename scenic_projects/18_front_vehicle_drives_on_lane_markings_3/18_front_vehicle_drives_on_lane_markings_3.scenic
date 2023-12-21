# Ego drives on the right lane and intends to change to the middle lane, front vehicle on the right lane drives on the lane marking on the left

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town04.xodr")
param carla_map = 'Town04'
param weather = "ClearNoon"
model scenic.simulators.carla.model 

roadSec = network.elements['road6'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

behavior EgoBehavior(target_speed=10, change_time=8):
    do FollowLaneBehavior(target_speed=target_speed) for change_time seconds
    do LaneChangeBehavior(
            laneSectionToSwitch=self.laneSection.laneToLeft,
            target_speed=target_speed)
    do FollowLaneBehavior(target_speed=target_speed)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 1, \
            with behavior EgoBehavior(target_speed=3), \
            facing 0 deg relative to roadDirection, \
            with FollowLaneBehavior(), \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"

        # langechange car
        target_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        spot = new OrientedPoint following roadDirection from target_spot for 10
        langechange_car = new Car on spot, \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.volkswagen.t2', \
                        with behavior FollowLeftEdgeBehavior()

# require (distance to intersection) > 10
# TODO specify intersection

terminate after 240 seconds
terminate when (distance from ego to spot) > 100 # in case ego never breaks

