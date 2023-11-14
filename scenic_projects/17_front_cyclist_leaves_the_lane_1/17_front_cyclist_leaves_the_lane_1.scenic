# Ego follows lane, front cyclist leaves the lane to the bus station on the right

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model 

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

# behavior CyclistBehavior():
#     try:
#         do ConstantThrottleBehavior()
#     interrupt when (distance from self to bus_stop) < 5:
#         take SetBrakeAction(1.0)

scenario OneBusStop(gap=0.25):
    precondition: ego.laneGroup._shoulder != None
    setup:
        spot = new OrientedPoint on visible ego.laneGroup.curb
        parkedCar = new BusStop left of spot by gap

scenario OneCyclist():
    setup:
        lane = ego.laneGroup.lanes[0]
        cyslist_spot = new OrientedPoint on visible lane.centerline
        cyclist = new Bicycle on cyslist_spot, \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior ConstantThrottleBehavior(0.5)

scenario Main():
    setup:
        # Ego car
        ego = new Car in roadSec.backwardLanes[1], \
            facing 0 deg relative to roadDirection, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"
        # bus stop
        # 
        # bus_stop = new Car on visible ego.laneGroup.curb
        # front cyclist
        
    compose:
        sce1 = OneBusStop()
        sce2 = OneCyclist()
        do sce1, sce2
        

require (distance from ego to intersection) < 5
terminate after 120 seconds

