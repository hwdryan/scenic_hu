from scenic.miscs.requirements import Requirements

current_logfile = "/home/weidonghu/Documents/data_2024_04_06_11_42_20.csv"
requirements = Requirements(current_logfile)
rbs=dict()

rbs['minimum_distance'] = requirements.minimum_distance()
rbs['exceed_acceleration'] = requirements.exceed_acceleration()

print(rbs)
