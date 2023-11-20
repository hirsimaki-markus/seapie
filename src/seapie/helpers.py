"""helper functions that do not belong in other places"""

import linecache
import os
import sys

from .state import __STATE__, STATE
from .version import __version__


def escape_frame(frame):
    """Escapes n frames up if required by state

    returns the "active" frame. ehkä nimeä tänne active frame?
    """
    # original_frame = frame
    for _ in range(STATE["callstack_escape_level"]):
        if frame.f_back is None:  # Check if end of stack reached
            # frame = original_frame
            STATE["callstack_escape_level"] -= 1
            print(
                "Callstack was too short for new escape level. Decrementing"
                " level by one. Level is now"
                f" {STATE['callstack_escape_level']}."
            )
            # break
        else:
            frame = frame.f_back
    return frame


def step_until_condition(frame):
    """Automatically steps if current state have an expression to check"""
    user_expression = STATE["step_until_expression"]
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
        STATE["step_until_expression"] = None
        return False
    else:
        if result:
            STATE["step_until_expression"] = None
            return False  # can stop stepping
        else:
            return True


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


def create_seapie_dir():
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
                f.write(__version__)
        except OSError as e:
            print(f"Error creating version file: {e}")
            return
        else:
            print("Initialized .seapie version file in", version_file)


def init_seapie_dir_and_reset_state():
    """Resets current state, creates seapie dir if not exists and ensures
    rw
    """
    STATE.update(__STATE__)
    create_seapie_dir()
    check_rw_access()


def update_magic_vars(current_frame, event, arg):
    # inject useful variables to the frame. this change should propagate
    # since we are in trace function. and running 3.12.
    # this must happen before exec (i think)
    # otherwise we would need
    # ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame),
    # ctypes.c_int(1))
    # maybe. or it works because we are in the trace function.
    if not STATE["inject_magic"]:
        return

    accum = []
    callstack_frame = current_frame
    while callstack_frame:
        accum.append(callstack_frame.f_code.co_name)
        callstack_frame = callstack_frame.f_back

    current_frame.f_locals["__callstack__"] = list(reversed(accum))

    current_frame.f_locals["__lineno__"] = current_frame.f_lineno

    # current_frame.f_locals["__scope__"] = current_frame.f_code.co_name

    current_frame.f_locals["__event__"] = event

    try:
        filename = current_frame.f_code.co_filename
        lineno = current_frame.f_lineno
        current_line = linecache.getline(filename, lineno)
        source = current_line.strip()
    except Exception:
        source = None
    current_frame.f_locals["__source__"] = source

    if event == "return":
        current_frame.f_locals["__returnval__"] = arg
    else:
        current_frame.f_locals["__returnval__"] = None

    if event == "exception":
        current_frame.f_locals["__exception__"] = arg[1]
    else:
        current_frame.f_locals["__exception__"] = None
    # NOTE: THE CONNECTION BETWEEN THESE MAGIC VALUES AND THE STATUS BAR
    # IS MAINTAINED MANUALLY IN SOURCE. THESE ARE NOT PASSED AS ARGS.
    # i.e: status bar could use different names and definitions.


def print_start_banner():
    invert = "\x1b[7m"  # invert color
    reset = "\x1b[0m"  # reset color
    banner = f"""
                {invert} ╒════════════════════╕ {reset}
                {invert}    ┏┓ ┏┓ ┏┓ ┏┓  ╻ ┏┓   {reset}
                {invert}    ┗┓ ┣┛ ┏┫ ┣┛ ╺┓ ┣┛   {reset}
                {invert}    ┗┛ ┗┛ ┗┛ ╹   ╹ ┗┛   {reset}
                {invert} ╘════════════════════╛ {reset}
    """
    print(banner)
    print("Enter !help or !h for help. See status bar at the top for info.")
