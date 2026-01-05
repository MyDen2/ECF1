import os

def ensure_dir_exists(path_dir):
    """Ensure the directory at 'path' exists; create it if necessary."""
    
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
        print(f"Created directory: '{path_dir}'")
    else:
        print(f"Directory already exists: '{path_dir}'")

    print(f"\nEnsure '{path_dir}'........................................[ok]\n")
    