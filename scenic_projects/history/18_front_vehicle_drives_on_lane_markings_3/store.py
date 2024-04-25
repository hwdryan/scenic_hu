import scenic, tempfile, pathlib, os
from scenic.simulators.carla import CarlaSimulator

scenic_dir = '18_front_vehicle_drives_on_lane_markings_3/'
scenic_path = '18_front_vehicle_drives_on_lane_markings_3.scenic'
scenic_param = 'param.scene'
scenic_path = os.path.join(scenic_dir, scenic_path)
scenic_param = os.path.join(scenic_dir, scenic_param)

map_path="../assets/maps/CARLA/Town04.xodr"
carla_map='Town04'
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

# scene, _ = scenario.generate()
# # safe parameters
# data = scenario.sceneToBytes(scene)
# with open(scenic_param, 'wb') as f:
#         f.write(data)
# simulator.simulate(scene, verbosity=2)

