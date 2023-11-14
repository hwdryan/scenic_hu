param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model 

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

scenario Main():
    setup:
        # Ego car
        ego = new Car in roadSec.forwardLanes[0], \
            with behavior FollowLaneBehavior(), \
            facing 0 deg relative to roadDirection, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"

        # langechange car
        lane = ego.laneGroup.lanes[0]
        spot = new OrientedPoint on visible lane.centerline 
        langechange_car = new Car on spot, \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.volkswagen.t2', \
                        with behavior FollowRightEdgeBehavior()

# require (distance to intersection) > 10
# TODO specify intersection
require (distance from ego to intersection) < 1

terminate after 240 seconds
terminate when (distance from ego to spot) > 100 # in case ego never breaks

