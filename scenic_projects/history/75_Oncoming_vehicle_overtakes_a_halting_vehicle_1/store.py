import scenic, tempfile, pathlib, os
from scenic.simulators.carla import CarlaSimulator

scenic_dir = '75_Oncoming_vehicle_overtakes_a_halting_vehicle_1/'
scenic_path = '75_Oncoming_vehicle_overtakes_a_halting_vehicle_1.scenic'
scenic_param = 'param.scene'
scenic_path = os.path.join(scenic_dir, scenic_path)
scenic_param = os.path.join(scenic_dir, scenic_param)

map_path="../assets/maps/CARLA/Town01.xodr"
carla_map='Town01'
weather="ClearNoon"
model="scenic.simulators.carla.model"



simulator = CarlaSimulator(carla_map=carla_map, 
                        map_path=map_path, 
                        )

scenario = scenic.scenarioFromFile(path = scenic_path
                                , params={"map":map_path
                                        , "carla_map":carla_map
                                        , "weather":weather}
                                , model=model
                                , mode2D=True)

scene, _ = scenario.generate()
# safe parameters
data = scenario.sceneToBytes(scene)
with open(scenic_param, 'wb') as f:
        f.write(data)
simulator.simulate(scene, verbosity=2)

