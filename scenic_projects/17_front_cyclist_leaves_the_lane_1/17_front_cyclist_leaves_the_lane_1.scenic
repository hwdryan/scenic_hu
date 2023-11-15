# Ego follows lane, front cyclist leaves the lane to the bus station on the right

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'
inter = network.elements['road809'].sections[0]



require (distance from ego to inter) < 1
require (distance from cyclist to inter) > 1
require (distance from cyclist to inter) < 3
require (distance from busstop to inter) > 15


behavior CyclistBehavior(target_speed=10,avoidance_threshold=10):
    try:
        do FollowLaneBehavior(target_speed=target_speed)
    interrupt when self.distanceToClosest(_model.BusStop) <= avoidance_threshold:
        shoulder_laneSce = self.laneSection
        shoulder_lane = self.laneSection.group._shoulder
        do LaneChangeToShoulderBehavior(
                laneSectionToSwitch=shoulder_laneSce,
                target_speed=target_speed)
        do FollowLaneBehavior(
                target_speed=target_speed,
                laneToFollow=shoulder_lane) 

scenario OneBusStop(gap=0.25):
    precondition: ego.laneGroup._shoulder != None
    setup:
        spot = new OrientedPoint on visible ego.laneGroup.curb
        busstop = new BusStop left of spot by gap

# scenario OneCyclist():
#     setup:
        
scenario Main():
    setup:
        # Ego car
        ego = new Car in roadSec.forwardLanes[0], \
            facing 0 deg relative to roadDirection, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"

        # front cyclist
        lane = ego.laneGroup.lanes[0]
        cyslist_spot = new OrientedPoint on visible lane.centerline
        cyclist = new Bicycle on cyslist_spot, \

                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior CyclistBehavior()

        
    compose:
        sce1 = OneBusStop()
        do sce1
        



terminate when (distance from cyclist to intersection) < 5

