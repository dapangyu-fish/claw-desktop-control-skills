import os
import sys

def get_project_root():
    """Returns the absolute path to the project root directory."""
    # Assuming this file is in scripts/utils.py, so project root is one level up
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_script_path(script_name):
    """Returns the absolute path to a script in the scripts directory."""
    return os.path.join(get_project_root(), 'scripts', script_name)

def add_project_root_to_sys_path():
    """Adds the project root to sys.path to allow importing modules from root."""
    project_root = get_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
