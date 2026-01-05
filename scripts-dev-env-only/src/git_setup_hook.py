"""
git_setup_hook.py

This script automatically sets up a Git hook in the current repository when executed.

Usage:
    python git_setup_hook.py

Environment:
    - os: windows 11
    - python version: 3.14.0
    - git version: 2.51.1.windows.1
Warning: It will probably need to be adapted if the environment changes.

Note:
This script needs to be run only once per repository.
The hook will then be triggered automatically on every git command which trigger it (e.g. `git commit` command to 
trigger 'commit-msg' hook).
"""

import os
from pathlib import Path
import re
import sys


from utils.utils_funcs_git_setup_hook import get_my_hooks_dir


# =================================================================================================================
#                                                   CONFIG.                            
# =================================================================================================================
REPO_PATH = os.getcwd() # Get the current working directory (should be the root of the repo)
HOOKS_DIR = os.path.join(REPO_PATH, '.git', 'hooks') # Path to the .git/hooks directory
MY_HOOKS_DIR = get_my_hooks_dir(REPO_PATH)
# print("MY_HOOKS_DIR:", MY_HOOKS_DIR)


# =================================================================================================================
#                                                   FUNCTIONS                            
# =================================================================================================================
def check_if_we_are_inside_a_git_repository():
    """Check if the current working directory is a git repository"""
    current_working_dir = os.path.join(REPO_PATH, '.git')
    
    if not os.path.isdir(current_working_dir):
        print(f"\nError: '{REPO_PATH}' is not a Git repository. Please navigate to the root of your Git repo.")
        sys.exit(1)

    print(f"\ncurrent working dir: '{current_working_dir}'")
    print("check if the current working directory is a git repository........................................[ok]\n")

def check_my_hooks_dir(): # MY_HOOKS_DIR
    """Check if 'my hooks' dir exists and not empty"""

    if not os.path.isdir(MY_HOOKS_DIR):
        print(f"\nError: Git hooks directory ({MY_HOOKS_DIR}) does not exists!")
        sys.exit(1)
    if not os.listdir(MY_HOOKS_DIR):
        print(f"\nError: Git hooks directory ({MY_HOOKS_DIR}) is empty.")
        sys.exit(1)
    print(f"\nmy hooks dir: '{MY_HOOKS_DIR}'")
    print(f"check if 'my hooks' dir exists and not empty........................................[ok]\n")

def choose_hook_to_set_up(): # from MY_HOOKS_DIR
    """Choose hook to set up based in existant hooks directories"""

    # List all directories at depth 1
    my_hooks_dirs = [name for name in os.listdir(MY_HOOKS_DIR) if os.path.isdir(os.path.join(MY_HOOKS_DIR, name))]
    
    # Create a dictionary with index as the key
    my_hooks_dirs_dict = {str(i+1): my_hooks_dirs[i] for i in range(len(my_hooks_dirs))}
    # print("my_hooks_dirs_dict:", my_hooks_dirs_dict)

    # Check if there is one or many hooks dirs
    if len(my_hooks_dirs_dict) == 0:
        print(f"\nError: There is no hook folder in '{my_hooks_dirs}'. Please create hooks folder like it's described in README.md")
        sys.exit(1)

    print("\nExisting hooks list: \n")

    for key, value in my_hooks_dirs_dict.items():
        print(key + ": "+ value)

    while(1):

        choose_hook_to_set_up = input("\nSet number of hook to setup (1 or 2 or ... or q to exit): ")
        
        if choose_hook_to_set_up == 'q':
            print("\nYou choosed 'q' to exit. See you, bye!")
            sys.exit(0) # end the script with succes status

        elif choose_hook_to_set_up in my_hooks_dirs_dict: # as key
            print(f"\n-----> Setup hook '{my_hooks_dirs_dict[choose_hook_to_set_up]}' ... \n")
            return my_hooks_dirs_dict[choose_hook_to_set_up]
        
        else:
            print(f"\nError: number of hook not exists: '{choose_hook_to_set_up}'")
        

def is_valid_hook_filename(filename: str) -> bool:
    """
    Check if filename follows: my_<commit-name>_v<number>
    Example: my_commit-msg_v10
    """
    pattern = r"^my_[a-zA-Z0-9_-]+_v\d+$"
    return bool(re.match(pattern, filename))

def check_my_hook_script_files_in_my_hook_dir(my_hook_dir: str)-> list: # in my_hook_dir
    """
    For every file of hook scripts:
    - check naming convention: my_<commit name>_v<nbr of vertion>. Example: my_commit-msg_v10
    - check existance of description file with the same pattern with '_description' at the end. Example: my_commit-msg_v10_description
    - check content of each description file: must starts and ends with special chars (===...)
    Returns:
        valid_files: list of files that are valid (name is ok) AND have description (have valid file description in the same dir)
    """

    invalid_files = []        # not valid file name
    missing_descriptions = [] # valid file name but missing discription file
    valid_files = []          # valid file (name is valid + have desctiption file)
    invalid_descriptions = [] # desc. file without """ at the start and end lines

    # List only files
    all_files = [f for f in os.listdir(my_hook_dir) if os.path.isfile(os.path.join(my_hook_dir, f))]

    for f in all_files:
        
        # Skip description files themselves
        if f.endswith("_description"):
            continue
        
        # 1) Filename check
        if not is_valid_hook_filename(f):
            invalid_files.append(f)
            continue
        
        desc_file = f"{f}_description"
        desc_path = os.path.join(my_hook_dir, desc_file)

        # 2️) Description existence check
        if desc_file not in all_files:
            missing_descriptions.append(f)
            continue

        # 3️) Description content check
        path_desc_file = Path(desc_path)
        content = Path(path_desc_file).read_text(encoding="utf-8").strip()
        # print(content)

        if not (content.startswith('===========================================================================================================================') and content.endswith('===========================================================================================================================')):
            invalid_descriptions.append(desc_file)
            continue
        # print("invalid_descriptions: ", invalid_descriptions)

        # Fully valid
        valid_files.append(f)

    if invalid_files:
        print(f"\nError: the hook dir '{my_hook_dir}' contains invalid hook files name: {invalid_files}")
        print(f"=> Each hook file must respecte the convention my_<commit name>_v<nbr of vertion>. Example: my_commit-msg_v10\n")
        sys.exit(1)

    if missing_descriptions:
        print(f"\nError: the hook dir '{my_hook_dir}' contains missing hook files description for: {missing_descriptions}")
        print("=> Each hook file must have a description file in the same directory. Example: 'my_commit_msg_v10' must have" \
        " it description file 'my_commit_msg_v10_description'\n")
        sys.exit(1)

    if invalid_descriptions:
        print(f"\nError: the hook dir '{my_hook_dir}' contains invalid description files content: {invalid_descriptions}")
        print('=> Each description file must: \n-starts with: =============================================================================================================\n-ends with:   =============================================================================================================\n')
        sys.exit(1)

    print(f"\nmy hook directory: {my_hook_dir}")
    print(f"check the validity of hook files in my hook directory........................................[ok]\n")
    return valid_files

def get_valid_versions_data(hook_to_setup_name: str, valid_files: list) -> dict:

    valid_versions = {}

    for file_name in valid_files:
        match = re.search(r"_v(\d+)$", file_name)
        if not match:
            continue

        version_number = match.group(1)
        version_key = f"version {version_number}"

        valid_versions[version_key] = {
            "version_number": version_number,
            "script_path": os.path.join(MY_HOOKS_DIR, hook_to_setup_name, file_name),
            "description_path": os.path.join(MY_HOOKS_DIR, hook_to_setup_name, file_name + "_description")
        }

    return valid_versions


# def choose_hook_version(valid_hook_versions_data: dict) -> str:
def choose_hook_version(hook_to_setup_name: str, valid_hook_versions_data: dict) -> dict:
    """
    Ask user to choose a hook version.
    
    Input:
        valid_hook_versions_data: dict. Example: {'version 1': {version_number: '1', script_path': '', 'description_path': ''}, 'version 2': {version_number: '2', 'script_path': '', 'description_path': ''}, }
    Returns:
        chosen_hook_version_data: dict. Ecample: {'version 2': {'version_number': '2', 'script_path': '', 'description_path': ''}}
    """

    print(f"\n'{hook_to_setup_name}' hook existing versions:\n")
    for version, data in valid_hook_versions_data.items():
        print(str(version).upper() + ":")
        print(Path(data["description_path"]).read_text(encoding="utf-8"))

    while(1):
        chosen_hook_version = input(f"=> Set number version of '{hook_to_setup_name}' hook to set up (1, or 2 or ...or q to exit): ")

        if any(data.get("version_number") == str(chosen_hook_version) for data in valid_hook_versions_data.values()) == True:
            # print("exists")
            for key, data in valid_hook_versions_data.items():
                if data['version_number'] == chosen_hook_version:
                    chosen_hook_version_data = {key: data}
                    break
            else:
                chosen_hook_version_data = {}

            return chosen_hook_version_data
        
        elif str(chosen_hook_version) == 'q':
            print("\nYou choosed 'q' to exit. See you, bye!")
            sys.exit(0) # end the script with succes status

        else:
            print(f"\nError: version number not exists: '{chosen_hook_version}'")

def create_new_hook(hook_to_setup_name: str, hook_path: str, my_hook_scipt_content: str): # from scratch
    """Create new or override the hook (if already exists)"""

    print(f"\nCreating the '{hook_to_setup_name}' hook ...")

    # Write the bash script content to the hook file
    with open(hook_path, 'w', encoding="utf-8") as f:
        f.write(my_hook_scipt_content)

    # Make the hook executable in .git
    os.chmod(hook_path, 0o755)
    print("Add permission '755' to 'commit-msg'.")

    print(f"The '{hook_to_setup_name}' hook was successfully created.")


def create_hook(hook_to_setup_name: str, choosed_hook_version_data: dict):
    """Create hook"""

    # print("\nchoosed_hook_version_data: ", choosed_hook_version_data)

    if not os.path.exists(HOOKS_DIR):
        print(f"\nError: Git hooks directory ({HOOKS_DIR}) does not exists!")
        sys.exit(1)

    print(f"\ngit hooks directory: {HOOKS_DIR}")
    print(f"check git hooks directory........................................[ok]\n")

    # Get content of the script to put in hook file (in .git/hooks/<hook name> file
    my_hook_script_path = next(iter(choosed_hook_version_data.values()))['script_path']
    my_hook_scipt_content = Path(my_hook_script_path).read_text(encoding="utf-8")
    # print("scipt_content: ", scipt_content)

    # Get hook_path (in .git)
    hook_path = os.path.join(HOOKS_DIR, hook_to_setup_name)
    
    # Check if the hook already exists in .git
    if os.path.exists(hook_path):
        print(f"The hook '{hook_to_setup_name}' already exists.")

        while(1):

            override_hook = input("\nDo you want to override it? (yes/no): ").lower()

            if override_hook == "yes":
                print(f"\nYour choice is 'yes': overriding '{hook_to_setup_name}' hook ...")
                create_new_hook(hook_to_setup_name, hook_path, my_hook_scipt_content)
                break
            elif override_hook == "no":
                print(f"\nYour choice is 'no': the hook '{hook_to_setup_name}'  will not be overrided.")
                break
            else:
                print(f"\nError: your choice is not valid: '{override_hook}'")
    else:
        create_new_hook(hook_to_setup_name, hook_path, my_hook_scipt_content)

# =================================================================================================================
#                                                   MAIN                            
# =================================================================================================================
def main():

    # === Verify if we are inside a Git repository
    check_if_we_are_inside_a_git_repository()
    
    # === Verify "my hooks dir": it must exists and not empty
    check_my_hooks_dir() # MY_HOOKS_DIR

    # === Choose hook to setup
    hook_to_setup_name = choose_hook_to_set_up()

    # === Define my hook dir based on hook_to_setup_name
    my_hook_dir = os.path.join(MY_HOOKS_DIR, hook_to_setup_name)

    # === Check hook dir content & get valid hook files
    valid_files = check_my_hook_script_files_in_my_hook_dir(my_hook_dir)
    # print("valid files list: ", valid_files)

    # === Extract data from valid files (file path + path of it description)
    valid_hook_versions_data = get_valid_versions_data(hook_to_setup_name, valid_files)
    # print("valid_hook_versions_data: ", valid_hook_versions_data)

    # === Ask user to choose a version data of hook to setup
    chosen_hook_version_data = choose_hook_version(hook_to_setup_name, valid_hook_versions_data)
    # print("chosen_hook_version_data: ", chosen_hook_version_data)

    # === Create hook in the Git repository
    create_hook(hook_to_setup_name, chosen_hook_version_data)

    print(f"\nThe Git '{hook_to_setup_name}' hook has been set up successfully!")

if __name__ == "__main__":
    main()