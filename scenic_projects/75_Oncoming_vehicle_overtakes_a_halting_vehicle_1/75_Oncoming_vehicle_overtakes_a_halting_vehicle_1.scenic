# The road has one lane for ego's travelling direction and one lane for the opposite direction. 
# On the opposite lane a delivery vehicle halts with warning flasher. The vehicle behind it performs overtaking via ego's lane.
param map = localPath("../../assets/maps/CARLA/Town01.xodr")
param carla_map = 'Town01'
param weather = "ClearSunset"
model scenic.simulators.carla.model
import scenic.simulators.carla.model as _model
import scenic.domains.driving.roads as _roads
import carla

roadSec = network.elements['road12'].sections[0]
ego_car_type = 'vehicle.tesla.model3'
truck_type = 'vehicle.mercedes.sprinter'

sidewalk_middle = new OrientedPoint on roadSec.road.laneGroups[0].sidewalk.centerline.middle
ped_spot = new OrientedPoint behind sidewalk_middle by 3, facing 0 deg relative to roadDirection

# self-defined
behavior VehicleLightBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetVehicleLightStateAction(carla.VehicleLightState(carla.VehicleLightState.RightBlinker | carla.VehicleLightState.LeftBlinker))

behavior OvertakeBehavior(target_speed=10,avoidance_threshold=20, bypass_dist=5):
    try:
        do FollowLaneBehavior(target_speed=target_speed)
    interrupt when self.distanceToClosest(Truck) <= 15:
        originalSec = self.laneSection
        laneToLeftSec = self.laneSection.laneToLeft
        do LaneChangeBehavior(
                laneSectionToSwitch=laneToLeftSec,
                is_oppositeTraffic=True,
                target_speed=target_speed)
        do FollowLaneBehavior(
                target_speed=target_speed,
                is_oppositeTraffic=True,
                laneToFollow=laneToLeftSec.lane) \
            until self.distanceToClosest(Truck) > bypass_dist
        do LaneChangeBehavior(
                laneSectionToSwitch=originalSec,
                target_speed=target_speed)
        do FollowLaneBehavior(target_speed=target_speed) for 2 seconds
        terminate

scenario Main():
    setup:
        # Ego car
        start_spot = new OrientedPoint on roadSec.forwardLanes[0].centerline.start
        ego = new Car following roadDirection from start_spot for 1, \
            facing 270 deg, \
            with blueprint ego_car_type, \
            with color Color(1,0,0), \
            with rolename "v1"
        
        # halting vehicle with warning flasher
        parked_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.middle
        parked_vehicle = new Truck on parked_vehicle_spot,  \
                        facing 90 deg, \
                        with blueprint truck_type, \
                        with behavior VehicleLightBehavior(), \
                        with rolename "van"

        # overtake vehicle
        overtake_vehicle_spot = new OrientedPoint on roadSec.backwardLanes[0].centerline.start
        overtake_vehicle = new Car following roadDirection from overtake_vehicle_spot for 1,  \
                        facing 90 deg, \
                        with blueprint ego_car_type, \
                        with rolename "target"