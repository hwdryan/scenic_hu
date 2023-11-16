# Ego follows lane, front cyclist leaves the lane to the bus station on the right

param map = localPath("C:/Tools/Scenic/assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'
# crosswalk = network.elements['road934'].sections[0]


behavior CyclistBehavior(target_speed=10,avoidance_threshold=18):
    try:
        do FollowLaneBehavior(target_speed=target_speed)
    interrupt when self.distanceToClosest(_model.BusStop) <= avoidance_threshold:
        shoulder_laneSce = self.laneSection
        # shoulder_lane = self.laneSection.group.shoulder
        nearby_intersection = self.laneSection.group._shoulder.centerline[-1]
        do LaneChangeToShoulderBehavior(
                laneSectionToSwitch=shoulder_laneSce,
                target_speed=target_speed)
        # do FollowShoulderBehavior(
        #         target_speed=target_speed,
        #         laneToFollow=shoulder_lane)
        terminate

scenario OneBusStop(gap=2.5):
    precondition: ego.laneGroup._shoulder != None
    setup:
        curb_start = new OrientedPoint on ego.laneGroup.curb.start
        bus_spot = new OrientedPoint behind curb_start by 38, facing 0 deg relative to roadDirection
        busstop = new BusStop left of bus_spot by gap

# scenario OneCyclist():
#     setup:
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 1, \
            with behavior FollowLaneBehavior(target_speed=3), \
            facing 0 deg relative to roadDirection, \
            with FollowLaneBehavior(), \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "hero"

        # front cyclist
        lane = ego.laneGroup.lanes[0]
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for 5
        cyclist = new Bicycle at cyslist_spot,  \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior CyclistBehavior()

        
    compose:
        sce1 = OneBusStop()
        do sce1
        

