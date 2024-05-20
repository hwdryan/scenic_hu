import os

# Specify the directory containing the folders
def rename_tcc_folders(directory, n:int):
    # Loop through the folder numbers from 1 to 8
    number = 8
    for i in range(0,100):
        if number == 0:
            break
        old_name = f"tcc{i}"
        new_name = f"tcc{i + n}"  # Adding 32 to the current number to get the new number
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        # Check if the old folder exists
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_name} to {new_name}")
            number-=1
        

def rename_tcl_folders(directory, n:int):
    # Loop through the folder numbers from 1 to 4
    number = 4
    for i in range(0,100):
        if number == 0:
            break
        old_name = f"tcl{i}"
        new_name = f"tcl{i + n}"  # Adding 32 to the current number to get the new number
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        # Check if the old folder exists
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_name} to {new_name}")
            number-=1

    print("Renaming completed.")

# change filename according to foldername
def rename_files_to_parent_folder(directory):
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            print(dir)
            for root, dirs, files in os.walk(os.path.join(directory,dir)):   
                for file in files:
                    file_path = os.path.join(root, file)
                    # Get the file extension
                    file_extension = os.path.splitext(file)[1]
                    # Get the parent folder name
                    parent_folder_name = os.path.basename(root)
                    print("parent_folder_name",parent_folder_name)
                    # Create the new file name with the parent folder name and original file extension
                    new_file_name = f"{parent_folder_name}{file_extension}"
                    print("new_file_name",new_file_name)
                    new_file_path = os.path.join(root, new_file_name)
                    print("new_file_path",new_file_path)
                    # Rename the file
                    os.rename(file_path, new_file_path)
                    print(f"Renamed '{file_path}' to '{new_file_path}'")

# Example usage
directory = "/home/weidong/Tools/Scenic/scenic_projects/nominal_scenario_catalog/nf2/nl3/nc6/tcc/Cyclist_crosses_from_the_roadside"
# rename_tcc_folders(directory,n=8)
# rename_tcl_folders(directory,n=4)
rename_files_to_parent_folder(directory)
