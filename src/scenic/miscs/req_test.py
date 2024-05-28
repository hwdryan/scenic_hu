from scenic.miscs.requirements import Requirements

current_logfile = "/home/weidonghu/Documents/data_2024_28_05_17_00_54.csv"
requirements = Requirements(current_logfile)
rbs=dict()

rbs = requirements.ego_being_overtaken()
print(rbs)
