"""
Prevent import this module outside a marker folder
"""
import os
import sys


marker = "src"
mypackage = "utils" # module name

# --- Dynamically find PROJECT_ROOT and MARKER_FOLDER ---
current = os.path.abspath(os.path.dirname(__file__))

while True:
    if marker in os.listdir(current):
        PROJECT_ROOT = current
        break
    parent = os.path.dirname(current)
    if parent == current:
        raise RuntimeError(f"Could not find project root containing '{marker}/'")
    current = parent

MARKER_FOLDER = os.path.join(PROJECT_ROOT, marker)
# print("MARKER_FOLDER:", MARKER_FOLDER)
PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
# print("PACKAGE_PATH:", PACKAGE_PATH)

# --- Ensure the package itself is inside marker/ ---
if not PACKAGE_PATH.startswith(MARKER_FOLDER):
    raise ImportError(
        f"'{mypackage}' package must be located inside the {marker}/ folder. "
        f"Current location: {PACKAGE_PATH}"
    )

# --- Ensure entry script is inside src/ ---
main = sys.modules.get("__main__")
caller_file = getattr(main, "__file__", None)

if caller_file is None:
    raise ImportError(
        f"'{mypackage}' cannot be imported interactively or without a main script"
    )

caller_file = os.path.abspath(caller_file)
# print("caller_file:", caller_file)

if not caller_file.startswith(MARKER_FOLDER):
    raise ImportError(
        f"'{mypackage}' can only be imported from scripts inside '{marker}/'. "
        f"Attempted from: {caller_file}"
    )


