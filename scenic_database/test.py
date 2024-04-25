import os

current_file_path = os.path.realpath(__file__).split("Scenic/")
print("Current file path:", current_file_path[-1])
