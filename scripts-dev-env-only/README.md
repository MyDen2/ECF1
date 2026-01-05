# scripts-dev-env-only
Useful scripts to be used only by developers in their development environment.

# Project structure
    scripts-dev-env-only
    |   .gitignore
    |   main.py
    |   README.md
    |   requirements.txt
    |   
    |       
    +---build
    |       scripts-dev-env-only.zip
    |       
    +---src
    |   |   git_setup_hook.py
    |   |   
    |   +---config
    |   |       config.yaml
    |   |       
    |   +---utils
    |   |      utils_funcs_git_setup_hook.py
    |   |      utils_funcs_global.py
    |   |      __init__.py
    |   |      
    |   |   
    |   |           
    |   |           
    |   |           
    |   +---workspace_git
    |       +---set_up_hooks
    |           +---my_hooks
    |               +---commit-msg
    |               |       my_commit_msg_v1
    |               |       my_commit_msg_v1_description
    |               |       
    |               +---pre-commit
    |                       my_pre_commit_v1
    |                       my_pre_commit_v1_description
    |                       my_pre_commit_v2
    |                       my_pre_commit_v2_description
    |                       
    +---utils
        utils_funcs.py
        __init__.py


## How to use it?
- Execute main.py and you will get a menu
- Choose the action you want to be executed

## Current actions
### 1. Create setup hook build
Create a zip build in /build directory

#### Structure of this build
    scripts-dev-env-only
    |   README.md
    |   requirements.txt
    |
    +---src
        |   git_setup_hook.py
        |   
        +---config
        |       config.yaml
        |       
        +---utils
        |       utils_funcs_git_setup_hook.py
        |       utils_funcs_global.py
        |       __init__.py
        |       
        +---workspace_git
            +---set_up_hooks
                +---my_hooks
                    +---commit-msg
                    |       my_commit_msg_v1
                    |       my_commit_msg_v1_description
                    |       
                    +---pre-commit
                            my_pre_commit_v1
                            my_pre_commit_v1_description
                            my_pre_commit_v2
                            my_pre_commit_v2_description

#### How to use this build
- Take the build **scripts-dev-env-only.zip** and unzip it
- Put the unzipped folder on the root of your project folder
- Ignore tracking **scripts-dev-env-only** folder (add **\*\*/scripts-dev-env-only/** to **.gitignore** file of your project folder)
- Install dependencies for this module from **requirements.txt** file: 
```bash
    > pip install -r <relatif path of requirements.txt file>
```
⚠️ **Warning:**: If your project runs in a **virtual environment**: To avoid polluting this **virtual environment** => Install this module's **dependencies** **outside** your project virtual environment and also, run the module scripts **outside** of it.

After that you will be able to execute useful scripts which contains **scripts-dev-env-only** folder.

##### Current scripts
###### 1 - git_setup_hook.py
```
Description:
This script automatically sets up a Git hook in the current repository when executed.

Usage:
    python <relatif path to git_setup_hook.py>
    
Environments:
    - os: windows 11
    - python version: 3.14.0
    - git version: 2.51.1.windows.1
Warning: It will probably need to be adapted if the environment changes.

Note:
This script needs to be run only once per repository.
The hook will then be triggered automatically on every git command which trigger it (e.g. `git commit` command to 
trigger 'commit-msg' hook).
```

###### *1.1 - my_commit_msg_\<version number>*
This script is used to create **commit-msg** hook in the default .git/hooks filder.

###### Current versions:
*my_commit_msg_v1:*

- Description in ./python/git/my_hooks/commit-msg/my_commit_msg_v1_description


##### *1.2 - my_pre-commit_v1*
This script is used to create **commit-msg** hook in the default .git/hooks folder.

###### Current versions:
*my_pre-commit_v1:*

- Description in ./python/git/my_hooks/pre-commit/my_pre_commit_v1_description

# Author
J.SAIDI
