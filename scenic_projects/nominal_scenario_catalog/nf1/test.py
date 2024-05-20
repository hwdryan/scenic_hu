import os
import re

def find_tcl_files(root_path):
    pattern = re.compile(r"tcc\d+\.scenic")  # Regular expression for matching "tcl" followed by digits

    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            if pattern.match(filename):
            # if "tcc" in filename and ".scenic" in filename:
                file_path = os.path.join(dirpath, filename)
                print("file_path",file_path)

if __name__ == "__main__":
    path = "/home/weidong/Tools/Scenic/scenic_projects/nominal_scenario_catalog/nf1/"  # Replace with your path
    find_tcl_files(path)
