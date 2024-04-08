# 1. One a straight road, there is a traffic jam on the lane opposite to ego's direction 

param map = localPath("../../assets/maps/CARLA/Town04.xodr")
param carla_map = 'Town04'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road15'].sections[0]
ego_car_type = 'vehicle.lincoln.mkz_2017'
parked_vehicle_type = [
    'vehicle.audi.a2',
    'vehicle.bmw.grandtourer',
    'vehicle.ford.crown',
    'vehicle.lincoln.mkz_2017',
    'vehicle.mini.cooper_s',
    'vehicle.audi.a2',
    'vehicle.bmw.grandtourer',
    'vehicle.ford.crown',
    'vehicle.lincoln.mkz_2017',
    'vehicle.mini.cooper_s',
    'vehicle.audi.a2',
    'vehicle.bmw.grandtourer',
    'vehicle.ford.crown',
    'vehicle.lincoln.mkz_2017',
    'vehicle.mini.cooper_s',
    'vehicle.audi.a2',
    'vehicle.bmw.grandtourer',
    'vehicle.ford.crown',
    'vehicle.lincoln.mkz_2017',
    'vehicle.mini.cooper_s',
]

        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for 30
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        
        ego = new Car following roadDirection from start_spot for 1, \
            with behavior FollowLaneBehavior(target_speed=4), \
            facing 0 deg relative to roadDirection, \
            with blueprint ego_car_type, \
            with color Color(0,0,0), \
            with rolename "hero"

        # Traffic jam
        parked_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start

        dis = 0
        for parked_vehicle in parked_vehicle_type:
            new Car following roadDirection from parked_vehicle_spot for dis,  \
                        with color Color(1,0,0), \
                        with blueprint parked_vehicle, \
                        with behavior BrakeBehavior()
            dis += 6


        

