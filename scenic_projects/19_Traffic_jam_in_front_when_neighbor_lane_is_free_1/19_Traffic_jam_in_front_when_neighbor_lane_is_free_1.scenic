# Uphill, neighbor lane is opposite to travelling direction. Oncoming traffic is unclear.

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model 

roadSec = network.elements['road41'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 0, \
            # with behavior FollowLaneBehavior(target_speed=3), \
            facing 0 deg relative to roadDirection, \
            with FollowLaneBehavior(), \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"

#         # langechange car
#         target_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
#         spot = new OrientedPoint following roadDirection from target_spot for 10
#         langechange_car = new Car on spot, \
#                         facing 0 deg relative to roadDirection, \
#                         with blueprint 'vehicle.volkswagen.t2', \
#                         with behavior FollowLeftEdgeBehavior()

# # require (distance to intersection) > 10
# # TODO specify intersection
# require (distance from ego to intersection) < 1

# terminate after 240 seconds
# terminate when (distance from ego to spot) > 100 # in case ego never breaks

