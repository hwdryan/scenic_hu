import os

script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the script
scenic_files = [file for file in os.listdir(script_dir) if file.endswith(".scenic")][0]
print(scenic_files)