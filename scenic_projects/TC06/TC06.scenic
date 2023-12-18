# roadwork in the middle, pedestrian walks diagonally

param map = localPath("../../assets/maps/CARLA/Town01.xodr")
param carla_map = 'Town01'
param weather = "ClearNoon"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads
import time

roadSec = network.elements['road15'].sections[0]
ego_car_type = 'vehicle.volkswagen.t2'
walker_type = 'walker.pedestrian.0006'
init_time = time.time()

# behavior 

# roadwork definition
scenario roadwork(gap=2.5):
    setup:
        road_middle = new OrientedPoint on roadSec.backwardLanes[0].leftEdge.middle
        cone1_pos = new OrientedPoint on road_middle, facing 0 deg relative to roadDirection
        cone1 = new ConstructionCone on cone1_pos
        cone2 = new ConstructionCone beyond cone1 by 1.5
        cone3 = new ConstructionCone beyond cone2 by 1.5
        cone4 = new ConstructionCone beyond cone3 by 1.5
        cone5_pos = new OrientedPoint beyond cone4 by 1.5
        cone5 = new ConstructionCone right of cone5_pos by 1.5
        cone6_pos = new OrientedPoint beyond cone1_pos by 1.5 from cone2
        cone6 = new ConstructionCone right of cone6_pos by 1.5
        
scenario Main():
    setup:
        # Ego car
            # with behavior FollowLaneBehavior(target_speed=3), \
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 1, \
            facing 0 deg relative to roadDirection, \
            with behavior FollowLaneBehavior(target_speed=3), \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "v1"

        # pedestrian walks diagonally
        # on ego.laneGroup.curb.middle
        curb_middle = new OrientedPoint on roadSec.road.laneGroups[1].curb.middle 
        ped_spot = new OrientedPoint on curb_middle, facing 0 deg relative to roadDirection

        # with behavior CrossingBehavior_s(reference_actor = ego, direction = 120 deg relative to ped_spot.heading, min_speed=0.5, threshold=30, final_speed=0.5), \
        # with behavior WalkwithDirectionBehavior(direction=120 deg relative to ped_spot.heading), \
        ped = new Pedestrian right of ped_spot by 0.1, \
            with behavior WalkwithDirectionBehavior(direction=120 deg relative to ped_spot.heading), \
            with blueprint walker_type

    compose:
        sce1 = roadwork()
        do sce1
        

