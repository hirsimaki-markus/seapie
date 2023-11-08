"""helper functions that do not belong in other places"""

import os
from .settings import CURRENT_SETTINGS
from .version import seapie_ver


def escape_frame(frame):
    """Escapes n frames up if required by settings

    returns the "active" frame. ehkä nimeä tänne active frame?
    """
    # original_frame = frame
    for _ in range(CURRENT_SETTINGS["callstack_escape_level"]):
        if frame.f_back is None:  # Check if end of stack reached
            # frame = original_frame
            CURRENT_SETTINGS["callstack_escape_level"] -= 1
            print(
                "Callstack was too short for new escape level. Decrementing"
                " level by one. Level is now"
                f" {CURRENT_SETTINGS['callstack_escape_level']}."
            )
            # break
        else:
            frame = frame.f_back
    return frame


def should_auto_step(frame):
    """Automatically steps if current settings have an expression to check"""
    user_expression = CURRENT_SETTINGS["step_until_expression"]
    if user_expression is None:  # no need to step. no expression set.
        return False
    try:
        result = bool(eval(user_expression, frame.f_globals, frame.f_locals))
    except NameError:  # ignore name errors, keep stepping.
        return True
    except Exception as e:
        print(
            "Conditional step failed with unexpected error:"
            f" {str(e)}. Clearing the expression."
        )
        CURRENT_SETTINGS["step_until_expression"] = None
        return False
    else:
        if result:
            return False  # can stop stepping
        else:
            return True


def should_simulate_user_input():
    """Returns empty string for false. Non empty string if should
    simulate."""
    if CURRENT_SETTINGS["echo_count"] > 0:
        CURRENT_SETTINGS["echo_count"] -= 1
        return CURRENT_SETTINGS["previous_bang"]
    else:
        return ""


def init_seapie_directory():
    """Creates"""
    path = os.path.expanduser("~")  # Get the writable path

    # Create the .seapie directory if it doesn't exist
    seapie_dir = os.path.join(path, ".seapie")
    if not os.path.exists(seapie_dir):
        try:
            os.makedirs(seapie_dir)
        except OSError as e:
            print(f"Error creating .seapie directory: {e}")
            return
        else:
            print("Initialized .seapie directory in", path)

    # Create the pickles, history, and snippets directories if they don't exist
    subdirectories = ["pickles", "history", "snippets"]
    for subdir in subdirectories:
        subdir_path = os.path.join(seapie_dir, subdir)
        if not os.path.exists(subdir_path):
            try:
                os.makedirs(subdir_path)
            except OSError as e:
                print(f"Error creating {subdir} directory: {e}")
                return
            else:
                print("Initialized .seapie subdirectory in", subdir_path)

    # Create the version file in the .seapie directory
    version_file = os.path.join(seapie_dir, "version")
    if not os.path.exists(version_file):
        try:
            with open(version_file, "w") as f:
                f.write(seapie_ver)
        except OSError as e:
            print(f"Error creating version file: {e}")
            return
        else:
            print("Initialized .seapie version file in", version_file)


def check_rw_access():
    """Checks read/write access on the files created in the
    init_seapie_directory() function.
    """
    path = os.path.expanduser("~")  # Get the writable path

    # Check read/write access on the .seapie directory
    seapie_dir = os.path.join(path, ".seapie")
    if not os.access(seapie_dir, os.R_OK | os.W_OK):
        print("No read/write access on .seapie directory:", seapie_dir)
        print("Aborting.")
        exit()

    # Check read/write access on the pickles, history, and snippets directories
    subdirectories = ["pickles", "history", "snippets"]
    for subdir in subdirectories:
        subdir_path = os.path.join(seapie_dir, subdir)
        if not os.access(subdir_path, os.R_OK | os.W_OK):
            print("No read/write access on", subdir, "directory:", subdir_path)
            print("Aborting.")
            exit()

    # Check read/write access on the version file
    version_file = os.path.join(seapie_dir, "version")
    if not os.access(version_file, os.R_OK | os.W_OK):
        print("No read/write access on version file:", version_file)
        print("Aborting.")
        exit()
