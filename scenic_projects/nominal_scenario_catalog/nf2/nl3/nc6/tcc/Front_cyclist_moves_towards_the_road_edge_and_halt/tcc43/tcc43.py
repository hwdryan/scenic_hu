from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
from datetime import datetime

# Change the current working directory to the specified directory
home_directory = os.path.expanduser('~')
directory_path = 'Tools/Scenic/scenic_projects'
os.chdir(os.path.join(home_directory,directory_path))
from scenic.simulators.carla import CarlaSimulator
from scenic.miscs.launches import launch_carla, launch_tools
from scenic.miscs.set_dreamview import set_dreamview, close_modules 
from scenic.miscs.requirements import Requirements

scenic_dir = os.path.join(home_directory, os.path.dirname(__file__))
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the script
scenic_path = [file for file in os.listdir(script_dir) if file.endswith(".scenic")][0]
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
        simulation = simulator.simulate(scene, verbosity=0, maxSteps=1500)
except Exception as e:
        print(e)
else:
        # Create an engine to connect to the database
        home_directory = os.path.expanduser('~')
        engine = create_engine(f'sqlite:///{home_directory}/Tools/Scenic/scenic_database/scenario_database.db', echo=True)

        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        home_dir = os.path.expanduser('~')
        dir_path = "~/Tools/Scenic/scenic_projects/nominal_scenario_catalog/"
        current_file_path = os.path.join(script_dir, scenic_path).replace(home_dir,"~")
        print("***current_file_path",current_file_path)
        
        test_case_queried = session.query(TestCase).join(TCEnhancedConcreteScenario).filter(TCEnhancedConcreteScenario.path == str(current_file_path)).first()
        
        required_behaviors = session.query(RequiredBehavior).\
                            join(RegulationRequiredBehavior).\
                            join(Regulation).\
                            join(RegulationTestCase).\
                            join(TestCase).\
                            join(TCEnhancedConcreteScenario).\
                            filter(TCEnhancedConcreteScenario.path == str(current_file_path)).all()
        
        requirements = Requirements(simulation.current_logfile)
        rbs=dict()
        for rb in required_behaviors:
                behavior = rb.behavior_name
                exec(f"rbs['{behavior}'] = requirements.{behavior}()")

        results = requirements.evaluate(rbs)

        # Get the current date and time
        current_datetime = datetime.now()
        test_result_1 = TestResult(system_info = "apollo v8.0.0",
                        test_result = results['conclusion'],
                        testing_date = current_datetime,
                        log_file = str(simulation.current_logfile))
        # one2many
        test_case_queried.test_result_items.append(test_result_1)
        # many2many
        hazardous_behaviors_queried = []
        for rb in required_behaviors:
                hazardous_behaviors_queried.append(session.query(HazardousBehavior).filter(HazardousBehavior.required_behavior == rb).first())
        test_result_1.hazardous_behaviors.extend(hazardous_behaviors_queried)


        session.add(test_result_1)
        session.commit()
        print("***results:",results)
finally:
        close_modules()

