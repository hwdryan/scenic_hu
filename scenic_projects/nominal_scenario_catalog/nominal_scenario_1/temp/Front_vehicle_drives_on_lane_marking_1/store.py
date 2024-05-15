import scenic, tempfile, pathlib, os

# Change the current working directory to the specified directory
home_directory = os.path.expanduser('~')
directory_path = 'Tools/Scenic/scenic_projects'
os.chdir(os.path.join(home_directory,directory_path))
from scenic.simulators.carla import CarlaSimulator
from scenic.miscs.launches import launch_carla, launch_tools
from scenic.miscs.set_dreamview import set_dreamview, close_modules 

scenic_dir = os.path.join(home_directory, os.path.dirname(__file__))
scenic_path = 'Front_vehicle_drives_on_lane_marking_1.scenic'
scenic_param = 'param.scene'
scenic_path = os.path.join(scenic_dir, scenic_path)
scenic_param = os.path.join(scenic_dir, scenic_param)

map_path="../assets/maps/CARLA/Town01.xodr"
carla_map='Town01'
weather="ClearNoon"
model="scenic.simulators.carla.model"

# 
try:
        launch_carla()
        simulator = CarlaSimulator(carla_map=carla_map, 
                                map_path=map_path, 
                                render=False
                                )

        scenario = scenic.scenarioFromFile(path = scenic_path
                                        , params={"map":map_path
                                                , "carla_map":carla_map
                                                , "weather":weather}
                                        , model=model
                                        , mode2D=True)

        scene, _ = scenario.generate()

        # save parameters
        data = scenario.sceneToBytes(scene)
        with open(scenic_param, 'wb') as f:
                f.write(data)

        # pipeline
        launch_tools()
        set_dreamview()
        simulator.simulate(scene, verbosity=2, maxSteps=1500)
finally:
        close_modules()
