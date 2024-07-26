# Ego follows lane, front cyclist leaves the lane to the bus station on the right

param map = localPath("../../assets/maps/CARLA/Town03.xodr")
param carla_map = 'Town03'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads

roadSec = network.elements['road3'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'

behavior CyclistBehavior(target_speed=10,avoidance_threshold=18):
    try:
        wait
    interrupt when self.EgoInitControl():
        try:
            # do FollowLaneBehavior(target_speed=target_speed)
            do AutopilotBehavior()
        interrupt when self.distanceToClosest(_model.BusStop) <= avoidance_threshold:
            shoulder_laneSce = self.laneSection
            # shoulder_lane = self.laneSection.group.shoulder
            nearby_intersection = self.laneSection.group._shoulder.centerline[-1]
            do LaneChangeToShoulderBehavior(
                    laneSectionToSwitch=shoulder_laneSce,
                    target_speed=target_speed)
            do AutopilotBehavior()
            # do FollowShoulderBehavior(
            #         target_speed=target_speed,
            #         laneToFollow=shoulder_lane)
            terminate

scenario OneBusStop(gap=2.5):
    setup:
        # curb_middle = new OrientedPoint on ego.laneGroup.curb.middle
        curb_middle = new OrientedPoint on roadSec.forwardLanes[0].group.curb.middle
        bus_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection
        busstop = new BusStop left of bus_spot by gap
        
scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego_spot = new OrientedPoint following roadDirection from start_spot for 1
        print(f"Ego position: {ego_spot.pos_and_ori()}")

        # ego = new Car following roadDirection from start_spot for 1, \
        #     with behavior FollowLaneBehavior(target_speed=3), \
        #     facing 0 deg relative to roadDirection, \
        #     with blueprint ego_car_type, \
        #     with color Color(1,0,0), \
        #     with rolename "hero"
    
        # front cyclist
        cyslist_spot = new OrientedPoint following roadDirection from start_spot for 15
        cyclist = new Bicycle at cyslist_spot,  \
                        facing 0 deg relative to roadDirection, \
                        with blueprint 'vehicle.bh.crossbike', \
                        with behavior CyclistBehavior()

        
    compose:
        sce1 = OneBusStop()
        do sce1
        

