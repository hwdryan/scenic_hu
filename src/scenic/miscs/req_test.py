from scenic.miscs.requirements import Requirements

current_logfile = "/home/weidong/Documents/data_2024_28_05_22_19_01.csv"
requirements = Requirements(current_logfile)
rbs=dict()

rbs = requirements.ego_being_overtaken()
print(rbs)
