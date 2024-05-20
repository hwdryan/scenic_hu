import os

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
                    # print(f"Renamed '{file_path}' to '{new_file_path}'")

# Example usage
directory = os.getcwd()
rename_files_to_parent_folder(directory)
