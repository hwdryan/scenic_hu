# 30 km/h zone, single road for two directions, vehicles parking on the roadsides. One pedestrian coming from behind of a parking vehicle to cross the road.
# vehicles parking on the roadsides. One pedestrian coming from behind of a parking vehicle to cross the road.
param map = localPath("../../assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'
walker_type = 'walker.pedestrian.0006'

sidewalk_middle = new OrientedPoint on roadSec.road.laneGroups[0].sidewalk.centerline.middle
ped_spot = new OrientedPoint behind sidewalk_middle by 3, facing 0 deg relative to roadDirection


behavior PedestrianBehavior(target_speed=10,avoidance_threshold=20):
    try:
        wait
    interrupt when self.distanceToObj(ego) <= avoidance_threshold:
        print("start walking!")
        do WalkwithDirectionBehavior(direction=270 deg relative to ped_spot.heading)

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 1, \
            with behavior FollowLaneBehavior(target_speed=3), \
            facing 0 deg relative to roadDirection, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"
        
        # parked vehicle
        parked_vehicle_spot = new OrientedPoint on roadSec.road.laneGroups[0].shoulder.centerline.middle
        parked_vehicle = new Car on parked_vehicle_spot,  \
                        facing 180 deg relative to roadDirection, \
                        with blueprint ego_car_type

        # pedestrian
        sidewalk_middle = new OrientedPoint on roadSec.road.laneGroups[0].sidewalk.centerline.middle
        # ped_spot = new OrientedPoint on sidewalk_middle, facing 0 deg relative to roadDirection
        ped_spot = new OrientedPoint behind sidewalk_middle by 3, facing 90 deg relative to roadDirection
        ped = new Pedestrian on ped_spot, \
            with behavior PedestrianBehavior