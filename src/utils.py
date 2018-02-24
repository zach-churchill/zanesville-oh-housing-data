import os
import sys
from pathlib import Path

def find_project_path(project_name):
    """Returns the full path for the project given that the project name is
    exactly how it is in the user's files and is in the path tree from the
    directory for which this function is called.

    Example
    --------
    If the project name is 'Project1', and the current directory that this
    function is '/home/zach/Documents/Project1/src/module1' then this function
    will return '/home/zach/Documents/Project1'.

    Parameters
    ----------
    project_name (str) : Name of the project, exactly how it is for the folder.

    Returns
    -------
    project_path (str) : The absolute path for the project if found; otherwise,
        error is printed to screen and program exited.

    """
    curr_dir = Path(os.getcwd())
    path_parts = curr_dir.parts

    try:
        project_part_index = path_parts.index(project_name)
    except ValueError as err:
        print(err)
        sys.exit()
    else:
        project_path = os.path.join(*path_parts[:project_part_index+1])

    return project_path
