"""Simulator interface for CARLA."""

try:
    import carla
except ImportError as e:
    raise ModuleNotFoundError('CARLA scenarios require the "carla" Python package') from e

import csv
import math
import json
import math
import os
import warnings
import psutil
import scenic.core.errors as errors

if errors.verbosityLevel == 0:  # suppress pygame advertisement at zero verbosity
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame

from scenic.core.simulators import SimulationCreationError, scenic_lead
from scenic.domains.driving.simulators import DrivingSimulation, DrivingSimulator
from scenic.simulators.carla.blueprints import oldBlueprintNames
import scenic.simulators.carla.utils.utils as utils
import scenic.simulators.carla.utils.visuals as visuals
from scenic.syntax.veneer import verbosePrint


class CarlaSimulator(DrivingSimulator):
    """Implementation of `Simulator` for CARLA."""

    def __init__(
        self,
        carla_map,
        map_path,
        # address="172.17.0.1",
        address="127.0.0.1",
        port=2000,
        timeout=10,
        render=True,
        record="",
        timestep=0.05,
        # timestep=None,
        traffic_manager_port=None,
    ):
        super().__init__()
        verbosePrint(f"Connecting to CARLA on port {port}")
        self.client = carla.Client(address, port)
        self.client.set_timeout(timeout)  # limits networking operations (seconds)
        if scenic_lead:
            # original way of load world
            if carla_map is not None:
                try:  
                    self.world = self.client.load_world(carla_map)
                except Exception as e:
                    raise RuntimeError(f"CARLA could not load world '{carla_map}'") from e
            else:
                if str(map_path).endswith(".xodr"):
                    with open(map_path) as odr_file:
                        self.world = self.client.generate_opendrive_world(odr_file.read())
                else:
                    raise RuntimeError("CARLA only supports OpenDrive maps")
            self.timestep = timestep
        else:
            # get world
            self.world = self.client.get_world()
            self.timestep = timestep

        if traffic_manager_port is None:
            traffic_manager_port = port + 6000
        check_and_kill_process_on_port(traffic_manager_port)
        check_and_kill_process_on_port(traffic_manager_port)
        check_and_kill_process_on_port(traffic_manager_port)
        self.tm = self.client.get_trafficmanager(traffic_manager_port)
        self.tm.set_synchronous_mode(True)

        # Set to synchronous with fixed timestep
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = timestep  # NOTE: Should not exceed 0.1
        self.world.apply_settings(settings)
        verbosePrint("Map loaded in simulator.")

        self.render = render  # visualization mode ON/OFF
        self.record = record  # whether to use the carla recorder
        self.scenario_number = 0  # Number of the scenario executed

    def createSimulation(self, scene, *, timestep, **kwargs):
        if timestep is not None and timestep != self.timestep:
            raise RuntimeError(
                "cannot customize timestep for individual CARLA simulations; "
                "set timestep when creating the CarlaSimulator instead"
            )

        self.scenario_number += 1
        return CarlaSimulation(
            scene,
            self.client,
            self.tm,
            self.render,
            self.record,
            self.scenario_number,
            timestep=self.timestep,
            **kwargs,
        )

    def destroy(self):
        super().destroy()
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None
        self.world.apply_settings(settings)
        self.tm.set_synchronous_mode(False)


class CarlaSimulation(DrivingSimulation):
    def __init__(self, scene, client, tm, render, record, scenario_number, **kwargs):
        self.client = client
        self.world = self.client.get_world()
        self.map = self.world.get_map()
        self.blueprintLib = self.world.get_blueprint_library()
        self.tm = tm
        self.render = render
        self.record = record
        self.scenario_number = scenario_number
        self.cameraManager = None
        self.t = None

        super().__init__(scene, **kwargs)

    def setup(self):
        weather = self.scene.params.get("weather")
        if weather is not None:
            if isinstance(weather, str):
                self.world.set_weather(getattr(carla.WeatherParameters, weather))
            elif isinstance(weather, dict):
                self.world.set_weather(carla.WeatherParameters(**weather))

        # Setup HUD
        if self.render:
            self.displayDim = (1280, 720)
            self.displayClock = pygame.time.Clock()
            self.camTransform = 0
            pygame.init()
            pygame.font.init()
            self.hud = visuals.HUD(*self.displayDim)
            self.display = pygame.display.set_mode(
                self.displayDim, pygame.HWSURFACE | pygame.DOUBLEBUF
            )
            self.cameraManager = None

        # if self.record:
        #     if not os.path.exists(self.record):
        #         os.mkdir(self.record)
        #     name = "{}/scenario{}.log".format(self.record, self.scenario_number)
        #     self.client.start_recorder(name)
        
        # self-defined
        user_home = os.path.expanduser("~")
        self.record = os.path.join(user_home,"Tools/Save/")
        if not os.path.exists(self.record):
            os.mkdir(self.record)
        name = "{}/scenario{}.log".format(self.record, self.scenario_number)
        self.client.start_recorder(name)

        # Create objects.
        super().setup()

        
        # self-defined
        if scenic_lead:
            # Set up camera manager and collision sensor for ego
            if self.render:
                camIndex = 0
                camPosIndex = 0
                egoActor = self.objects[0].carlaActor
                t = egoActor.get_transform()
                self.cameraManager = visuals.CameraManager(self.world, egoActor, self.hud)
                self.cameraManager._transform_index = camPosIndex
                self.cameraManager.set_sensor(camIndex)
                self.cameraManager.set_transform(self.camTransform)
        else:
            # self-defined
            world = self.client.get_world()
            for actor in world.get_actors():
                if actor.attributes.get('role_name') in ['autoware_v1', 'hero', 'ego_vehicle']:
                    egoActor = actor
    
        if scenic_lead:
            self.world.tick() 
        else:
            self.world.wait_for_tick()

        for obj in self.objects:
            if isinstance(obj.carlaActor, carla.Vehicle):
                obj.carlaActor.apply_control(
                    carla.VehicleControl(manual_gear_shift=False)
                )

        if scenic_lead:
            self.world.tick()
        else:
            self.world.wait_for_tick()

        for obj in self.objects:
            if obj.speed is not None and obj.speed != 0:
                raise RuntimeError(
                    f"object {obj} cannot have a nonzero initial speed "
                    "(this is not yet possible in CARLA)"
                )

    def createObjectInSimulator(self, obj):
        # Extract blueprint
        try:
            blueprint = self.blueprintLib.find(obj.blueprint)
        except IndexError as e:
            found = False
            if obj.blueprint in oldBlueprintNames:
                for oldName in oldBlueprintNames[obj.blueprint]:
                    try:
                        blueprint = self.blueprintLib.find(oldName)
                        found = True
                        warnings.warn(
                            f"CARLA blueprint {obj.blueprint} not found; "
                            f"using older version {oldName}"
                        )
                        obj.blueprint = oldName
                        break
                    except IndexError:
                        continue
            if not found:
                raise SimulationCreationError(
                    f"Unable to find blueprint {obj.blueprint}" f" for object {obj}"
                ) from e
        if obj.rolename is not None:
            blueprint.set_attribute("role_name", obj.rolename)

        # set walker as not invincible
        if blueprint.has_attribute("is_invincible"):
            blueprint.set_attribute("is_invincible", "False")

        # Set up transform
        loc = utils.scenicToCarlaLocation(
            obj.position, world=self.world, blueprint=obj.blueprint
        )
        rot = utils.scenicToCarlaRotation(obj.orientation)
        transform = carla.Transform(loc, rot)

        # Color, cannot be set for Pedestrians
        if blueprint.has_attribute("color") and obj.color is not None:
            c = obj.color
            c_str = f"{int(c.r*255)},{int(c.g*255)},{int(c.b*255)}"
            blueprint.set_attribute("color", c_str)

        # Create Carla actor
        carlaActor = self.world.try_spawn_actor(blueprint, transform)
        if carlaActor is None:
            raise SimulationCreationError(f"Unable to spawn object {obj}")
        obj.carlaActor = carlaActor

        carlaActor.set_simulate_physics(obj.physics)

        if isinstance(carlaActor, carla.Vehicle):
            # TODO should get dimensions at compile time, not simulation time
            extent = carlaActor.bounding_box.extent
            ex, ey, ez = extent.x, extent.y, extent.z
            # Ensure each extent is positive to work around CARLA issue #5841
            obj.width = ey * 2 if ey > 0 else obj.width
            obj.length = ex * 2 if ex > 0 else obj.length
            obj.height = ez * 2 if ez > 0 else obj.height
            carlaActor.apply_control(carla.VehicleControl(manual_gear_shift=True, gear=1))
        elif isinstance(carlaActor, carla.Walker):
            carlaActor.apply_control(carla.WalkerControl())
            # spawn walker controller
            controller_bp = self.blueprintLib.find("controller.ai.walker")
            controller = self.world.try_spawn_actor(
                controller_bp, carla.Transform(), carlaActor
            )
            if controller is None:
                raise SimulationCreationError(
                    f"Unable to spawn carla controller for object {obj}"
                )
            obj.carlaController = controller
        return carlaActor

    def executeActions(self, allActions):
        super().executeActions(allActions)

        # Apply control updates which were accumulated while executing the actions
        for obj in self.agents:
            ctrl = obj._control
            if ctrl is not None:
                obj.carlaActor.apply_control(ctrl)
                obj._control = None

    def step(self):
        
        # Run simulation for one timestep
        if scenic_lead:
            self.world.tick()
        else:
            world_snapshot = self.world.wait_for_tick()
            data = self.custom_recorder(world_snapshot)
        
        # Render simulation
        if self.render:
            self.cameraManager.render(self.display)
            pygame.display.flip()
        if scenic_lead:
            return None
        return data
            

    # self-defined
    def custom_recorder(self, world_snapshot):
        """
        get_acceleration(self)
            Returns the actor's 3D acceleration vector the client recieved during last tick. The method does not call the simulator.
            Return: carla.Vector3D - m/s2
        get_angular_velocity(self)
            Returns the actor's angular velocity vector the client recieved during last tick. The method does not call the simulator.
            Return: carla.Vector3D - deg/s
        get_location(self)
            Returns the actor's location the client recieved during last tick. The method does not call the simulator.
            Return: carla.Location - meters
            Setter: carla.Actor.set_location
        get_transform(self)
            Returns the actor's transform (location and rotation) the client recieved during last tick. The method does not call the simulator.
            Return: carla.Transform
            Setter: carla.Actor.set_transform
        get_velocity(self)
            Returns the actor's velocity vector the client recieved during last tick. The method does not call the simulator.
            Return: carla.Vector3D - m/s
        """
        user_home = os.path.expanduser("~")

        timestamp = world_snapshot.timestamp.elapsed_seconds
        actor_list = self.world.get_actors()
        vehicles = actor_list.filter('vehicle.*.*')
        peds = actor_list.filter('walker.pedestrian.*')
        current_map = self.world.get_map()
        # front_actor_id = actor_list.filter('vehicle.tesla.model3')[0].id
        # overtake_actor_id = actor_list.filter('vehicle.volkswagen.t2')[0].id
        home_directory = os.path.expanduser('~')
        config_path = os.path.join(home_directory, "Tools/apollo/modules/carla_bridge/config/objects.json")
        with open(config_path, 'r') as file:
            data = json.load(file)
        d_x = data['objects'][1]['destination_point']['x']
        d_y = data['objects'][1]['destination_point']['y']
        d_z = data['objects'][1]['destination_point']['z']
        ego_destination = tuple(map(float, [d_x,d_y,d_z]))
        bb = dict()
        data = dict()
        for group in (vehicles, peds):
            for v in group:
                actor = world_snapshot.find(v.id)
                actual_actor = self.world.get_actor(v.id)
                location = actor.get_transform().location
                location = tuple(map(float,[location.x, location.y, location.z]))
                rotation = actor.get_transform().rotation
                rotation = tuple(map(float,[rotation.pitch, rotation.yaw, rotation.roll]))
                angular_velocity = actor.get_angular_velocity()
                angular_velocity = tuple(map(float,[angular_velocity.x, angular_velocity.y, angular_velocity.z]))
                velocity = actor.get_velocity()
                velocity = tuple(map(float,[velocity.x, velocity.y, velocity.z]))
                acceleration = actor.get_acceleration()
                acceleration = tuple(map(float,[acceleration.x, acceleration.y, acceleration.z]))
                # 
                vehicle_lane_id = current_map.get_waypoint(actor.get_transform().location).lane_id

                vehicle_bb_location = [list(map(float,[v.x,v.y,v.z])) for v in actual_actor.bounding_box.get_world_vertices(actor.get_transform())][0::2]
                vehicle_bb_location[2], vehicle_bb_location[3] = vehicle_bb_location[3], vehicle_bb_location[2] 
                role_name = actual_actor.attributes.get('role_name')
                if role_name in ['autoware_v1', 'hero', 'ego_vehicle']:
                    role_name = 'ego'
                    bb['ego'] = vehicle_bb_location
                    data[role_name] = [[timestamp] + [int(v.id)] + [role_name] + [vehicle_lane_id] + list(location) + list(rotation) + list(angular_velocity) + list(velocity) + list(acceleration) + list(ego_destination)]
                else:
                    bb[role_name] = vehicle_bb_location
                    data[role_name] = [[timestamp] + [int(v.id)] + [role_name] + [vehicle_lane_id] + list(location) + list(rotation) + list(angular_velocity) + list(velocity) + list(acceleration) + list([None,None,None])]        

        def bb_size(bb_points):
            # calculate boundingbox size 
            length = 0
            width = 0
            size = []
            for a in bb_points:
                for b in bb_points:
                    size.append(euclidean_distance((a), b))
            size = [x for x in size if x>0]

            length = max(size)
            width = min(size)

        
            return (length,width)

        def euclidean_distance(point1, point2):
            """Calculate the Euclidean distance between two points."""
            return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)
        
        def distance_point2line(p_a,p_b,p_c):
            x_1 = p_a[0]
            y_1 = p_a[1]
            x_2 = p_b[0]
            y_2 = p_b[1]
            x_0 = p_c[0]
            y_0 = p_c[1]
            n_A = y_2 - y_1
            n_B = x_1 - x_2
            n_C = x_2*y_1 - x_1*y_2
            q_x = (n_B**2 * x_0 - n_A*n_B*y_0 - n_A*n_C)/(n_A**2 + n_B**2)
            q_y = (n_A**2 * y_0 - n_A*n_B*x_0 - n_B*n_C)/(n_A**2 + n_B**2)
            if q_x < min(x_1, x_2) or q_x > max(x_1, x_2):
                return math.inf
            if q_y < min(y_1, y_2) or q_y > max(y_1, y_2):
                return math.inf
            d = abs(n_A*x_0 + n_B*y_0 + n_C)/math.sqrt(n_A**2 + n_B**2)

            return d

        def vehicle_collide(v1_bb_location,v2_bb_location):
            """
            point (xp, yp), edge (x1, y1) - (x2, y2):
            D = (x2 - x1) * (yp - y1) - (xp - x1) * (y2 - y1)
            If D > 0, the point is on the left-hand side. If D < 0, the point is on the right-hand side. If D = 0, the point is on the line.
            """
            d_list1 = list()
            for p0 in v1_bb_location:
                d_point = list()
                for idx, p1 in enumerate(v2_bb_location):
                    p2 = v2_bb_location[(idx+1)%4]
                    d = (p2[0]-p1[0]) * (p0[1]-p1[1]) - (p0[0]-p1[0]) * (p2[1]-p1[1])
                    d_point.append(d)
                if max(d_point) <= 0:
                    return True
                d_list1.append(d_point)

            d_list2 = list()
            for p0 in v2_bb_location:
                d_point = list()
                for idx, p1 in enumerate(v1_bb_location):
                    p2 = v1_bb_location[(idx+1)%4]
                    d = (p2[0]-p1[0]) * (p0[1]-p1[1]) - (p0[0]-p1[0]) * (p2[1]-p1[1])
                    d_point.append(d)
                if max(d_point) <= 0:
                    return True
                d_list2.append(d_point)

            return False
        
        def calculate_distances(data):
            """Calculate distances from 'ego' to other points."""
            ego_points = data['ego']
            results = dict()
            
            for id, target_points in data.items():
                if id != 'ego':
                    distances = []
                    # Given ego_points and target_points, calculate if they overlap
                    if vehicle_collide(target_points,ego_points):
                        results[id] = 0
                        continue

                    for ego_point in ego_points:
                        for idx, target_point1 in enumerate(target_points):
                            for target_point2 in target_points[idx+1:]:
                                distances.append(distance_point2line(target_point1,target_point2,ego_point))

                    for target_point in target_points:
                        for idx, ego_point1 in enumerate(ego_points):
                            for ego_point2 in ego_points[idx+1:]:
                                distances.append(distance_point2line(ego_point1,ego_point2,target_point))

                    for ego_point in ego_points:
                        for point in target_points:
                            distances.append(euclidean_distance(ego_point, point))
                    
                    results[id] = min(distances)
                else:
                    results[id] = -100

            return results
                
        bb = calculate_distances(bb)

        for key in data:
            data[key][0].append(str(bb[key]))

        return data


    # TODO
    def _is_vehicle_hazard(self, vehicle_list):
        """

        :param vehicle_list: list of potential obstacle to check
        :return: a tuple given by (bool_flag, vehicle), where
                 - bool_flag is True if there is a vehicle ahead blocking us
                   and False otherwise
                 - vehicle is the blocker object itself
        """
        ego_vehicle_location = self._vehicle.get_location()
        ego_vehicle_waypoint = self._map.get_waypoint(ego_vehicle_location)

        longitudinal_acc = self._vehicle.get_acceleration().x
        ego_velocity = self._vehicle.get_velocity().x
        response_time = 0.8

        safe_distance = self._proximity_vehicle_threshold

        for target_vehicle in vehicle_list:

            # recalculate safe_distance
            if longitudinal_acc - target_vehicle.get_acceleration().x < 0.0:
                safe_distance = response_time * ego_velocity
                if safe_distance < self._proximity_vehicle_threshold:
                    safe_distance = self._proximity_vehicle_threshold
            # do not account for the ego vehicle
            if target_vehicle.id == self._vehicle.id:
                continue

            tv_vertices = target_vehicle.bounding_box.get_world_vertices(
                target_vehicle.get_transform())
            tv_vertices = [tv_vertices[0], tv_vertices[2], tv_vertices[4], tv_vertices[6]]
            tv_vertex_waypoints = [self._map.get_waypoint(vertex) for vertex in tv_vertices]

            # check if object vertices falls on ego lane
            extension_falls_on_ego_lane = False
            for tv_vertex_waypoint in tv_vertex_waypoints:
                if tv_vertex_waypoint.lane_id == ego_vehicle_waypoint.lane_id:
                    extension_falls_on_ego_lane = True

            # if the object is not in our lane it's not an obstacle
            target_vehicle_waypoint = self._map.get_waypoint(target_vehicle.get_location())
            if (target_vehicle_waypoint.road_id == ego_vehicle_waypoint.road_id and
                target_vehicle_waypoint.lane_id == ego_vehicle_waypoint.lane_id) or \
                    extension_falls_on_ego_lane:
                delta_p = self._vehicle.bounding_box.extent.x + target_vehicle.bounding_box.extent.x
                if is_within_distance_ahead(target_vehicle.get_transform(),
                                            self._vehicle.get_transform(),
                                            safe_distance + delta_p):
                    return True, target_vehicle

        return False, None


    def getProperties(self, obj, properties):
        if self.t == None:
            # Print ego position
            egoActor = self.objects[0].carlaActor
            self.t = egoActor.get_transform()
            # print("******")
            # print("******")
            # print("Ego position:", self.t)
            # print("******")
            # print("******")

        # Extract Carla properties
        carlaActor = obj.carlaActor
        currTransform = carlaActor.get_transform()
        currLoc = currTransform.location
        currRot = currTransform.rotation
        currVel = carlaActor.get_velocity()
        currAngVel = carlaActor.get_angular_velocity()

        # Prepare Scenic object properties
        position = utils.carlaToScenicPosition(currLoc)
        velocity = utils.carlaToScenicPosition(currVel)
        speed = math.hypot(*velocity)
        angularSpeed = utils.carlaToScenicAngularSpeed(currAngVel)
        angularVelocity = utils.carlaToScenicAngularVel(currAngVel)
        globalOrientation = utils.carlaToScenicOrientation(currRot)
        yaw, pitch, roll = obj.parentOrientation.localAnglesFor(globalOrientation)
        elevation = utils.carlaToScenicElevation(currLoc)

        values = dict(
            position=position,
            velocity=velocity,
            speed=speed,
            angularSpeed=angularSpeed,
            angularVelocity=angularVelocity,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            elevation=elevation,
        )
        return values

    def destroy(self):
        # # self-defined
        # print("***DESTROY***")
        # for actor in self.world.get_actors():
        #     if isinstance(actor, carla.Sensor):
        #         actor.stop()
        #         actor.destroy()
        # # 
        for obj in self.objects:
            if obj.carlaActor is not None:
                if isinstance(obj.carlaActor, carla.Vehicle):
                    obj.carlaActor.set_autopilot(False, self.tm.get_port())
                if isinstance(obj.carlaActor, carla.Walker):
                    obj.carlaController.stop()
                    obj.carlaController.destroy()
                obj.carlaActor.destroy()
        if self.render and self.cameraManager:
            self.cameraManager.destroy_sensor()
        
        # self-defined
        print(f"{len(self.world.get_actors())} are left to destroy")
        for actor in self.world.get_actors():
            if isinstance(actor, carla.Sensor):
                if actor.is_listening:
                    actor.stop()
            actor.destroy()
            
        
        self.client.stop_recorder()

        self.world.tick()

        super().destroy()


# self-defined
def check_and_kill_process_on_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            pid = conn.pid
            try:
                process = psutil.Process(pid)
                process.kill()
                print(f"Process with PID {pid} killed.")
            except psutil.NoSuchProcess:
                print(f"No such process with PID {pid}.")
            return
    print(f"No process found occupying port {port}.")

