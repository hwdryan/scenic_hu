from scenic.miscs.requirements import Requirements

current_logfile = "/home/weidong/Documents/data_2024_27_05_15_34_53.csv"
requirements = Requirements(current_logfile)
rbs=dict()

rbs = requirements.ego_safe_deceleration()
print(rbs)
