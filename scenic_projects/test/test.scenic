param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town01.xodr")
param carla_map = 'Town01'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road15'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 5, \
            facing 0 deg relative to roadDirection, \
            with behavior FollowLaneBehavior(), \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "test"
        

