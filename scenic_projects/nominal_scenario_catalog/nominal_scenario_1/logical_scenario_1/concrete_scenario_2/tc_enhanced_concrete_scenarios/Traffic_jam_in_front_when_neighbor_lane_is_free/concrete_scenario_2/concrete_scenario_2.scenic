# One a straight road, there is a traffic jam on the lane opposite to ego's direction 


################
# Scenic code
################
param map = localPath("../../assets/maps/CARLA/Town01.xodr")
param carla_map = 'Town01'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads
import scenic.simulators.carla.utils.utils as _utils
import scenic.simulators.carla.misc as _misc

roadSec = network.elements['road15'].sections[0]
target_vehicle_type = 'vehicle.lincoln.mkz_2017'
parked_vehicle_type = [
    'vehicle.audi.a2',
    'vehicle.bmw.grandtourer',
    'vehicle.ford.crown',
    'vehicle.lincoln.mkz_2017',
    'vehicle.mini.cooper_s',
]

# location of vehicles
road_length = 308.69
Ego_loc = 100
parked_vehicle_loc = 120
number_of_vehicle = 5

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc
        destination_spot = new OrientedPoint following roadDirection from start_spot for Ego_loc - 10
        print(f"Ego position: {ego_spot.pos_and_ori()}")
        print(f"Ego destination: {destination_spot.destination_spot()}")

        # Traffic jam
        parked_vehicle_spot = new OrientedPoint following roadDirection from start_spot for parked_vehicle_loc

        count = 0
        while count < number_of_vehicle:
            new Car following roadDirection from parked_vehicle_spot for (count*6),  \
                        with color Color(1,0,0), \
                        with blueprint parked_vehicle_type[count % len(parked_vehicle_type)], \
                        with behavior BrakeBehavior()
            count += 1



        

