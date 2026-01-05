import os
from pathlib import Path
import sys
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"

# print("CONFIG_PATH:", CONFIG_PATH)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


try:
    project_folder_name = config["app"]["name"]
    source_code_folder = config["app"]["source_code_folder"] # src
    workspace_git_folder_name = config["workspace_git"]["name"]
    set_up_hooks_action_folder_name = config["workspace_git"]["actions"]["set_up_hooks"]["folder_name"]
    my_hooks_dir_name = config["workspace_git"]["actions"]["set_up_hooks"]["additional_data"]["my_hooks_dir_name"] # my_hooks

except Exception as e:
    print(f"Can't extract data from config. file: {e}")

# print("project_folder_name:", project_folder_name)
# print("source_code_folder:", source_code_folder)
# print("workspace_git_folder_name:", workspace_git_folder_name)
# print("set_up_hooks_action_folder_name:", set_up_hooks_action_folder_name)
# print("my_hooks_dir_name:", my_hooks_dir_name)


def get_my_hooks_dir(repo_path: str):
    """
    Get a value to 'my hook dir' depending on the current repo: repo. source of scripts-dev-env-only or repo. of a project
    which use the scripts-dev-env-only tool.
    """
    path1 = os.path.join(repo_path, project_folder_name,  source_code_folder, workspace_git_folder_name, set_up_hooks_action_folder_name, my_hooks_dir_name) # repo. of a project which use the scripts-dev-env-only
    if os.path.exists(path1):
        return path1
    return os.path.join(repo_path, source_code_folder, workspace_git_folder_name, set_up_hooks_action_folder_name, my_hooks_dir_name) # repo. source of scripts-dev-env-only
    