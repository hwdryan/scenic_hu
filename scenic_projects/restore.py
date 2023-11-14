import scenic, tempfile, pathlib
from scenic.simulators.carla import CarlaSimulator

scenic_path = '/home/weidonghu/Desktop/python_projects/carla_autoware/17_front_vehicle_drives_on_lane_markings.scenic'
map_path="/home/weidonghu/Tools/Scenic/assets/maps/CARLA/Town03.xodr"
carla_map='Town03'
weather="ClearNoon"
model="scenic.simulators.carla.model"


simulator = CarlaSimulator(carla_map=carla_map, 
                        map_path=map_path, 
                        )

scenario = scenic.scenarioFromFile(path = scenic_path
                                , params={"map":"/home/weidonghu/Tools/Scenic/assets/maps/CARLA/Town03.xodr" 
                                        , "carla_map":'Town03'
                                        , "weather":"ClearNoon"}
                                , model="scenic.simulators.carla.model"
                                , mode2D=True)
with open('./test.scene', 'rb') as f:
    data = f.read()
scene = scenario.sceneFromBytes(data)
simulator.simulate(scene, verbosity=2)