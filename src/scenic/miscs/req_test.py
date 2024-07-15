from scenic.miscs.requirements import Requirements

current_logfile = "/home/weidonghu/Documents/data_2024_29_05_12_23_34.csv"
requirements = Requirements(current_logfile)
rbs=dict()

rbs = requirements.ego_being_overtaken()
print(rbs)
