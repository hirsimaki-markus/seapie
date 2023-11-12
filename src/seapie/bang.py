"""
bang handler stuff and related tools
"""

import os
import sys
import traceback
import pickle
from .settings import CURRENT_SETTINGS
from .status import get_status
from .status import print_pickles


def bang_handler(user_input, frame, event, arg):
    """Attempts to do complete adnlings of bands. returns values only

    if the enclosing repl must take an action that cant be done here.

    dokumentoi tai poista aliakset

    possible actions and return values:
    * exit() happens
    * step-with-repl; repl should return itself as the new trace func
    * continue-in-repl; repl loop should "continue" in while and read new input
    * step-without-repl

    input is case sensitive because !condition has to be case sensitive
    """
    original_input = user_input  # needed as arg for bangs that take args
    user_input = user_input.lower()

    if original_input.startswith("!"):  # save the bang
        if user_input.startswith("!e") or user_input.startswith("!echo"):
            pass  # echo bang is not saved to avoid infinite loop
        else:
            CURRENT_SETTINGS["previous_bang"] = original_input

    if user_input in ("!q", "!quit"):
        exit()
    elif user_input in ("!s", "!step"):
        if CURRENT_SETTINGS["callstack_escape_level"] != 0:
            CURRENT_SETTINGS["callstack_escape_level"] = 0
            print("Resetting escape level to 0 before stepping.")
        return "step-with-repl"
    elif user_input in ("!r", "!run"):
        frame.f_trace = None
        sys.settrace(None)
        return "step-without-repl"
    elif user_input in ("!h", "!help"):
        print_help()
        return "continue-in-repl"
    elif user_input in ("!t", "!traceback", "!tb"):
        print_tb(frame, 0)  # there are no seapie related frames to hide since
        # there is no exception going on.
        return "continue-in-repl"
    elif user_input in ("!b", "!bar"):
        CURRENT_SETTINGS["show_bar"] = not CURRENT_SETTINGS["show_bar"]
        if CURRENT_SETTINGS["show_bar"]:
            print("Bar on.")
        else:
            print("Bar off.")
        return "continue-in-repl"
    elif user_input in ("!m", "!magic"):
        CURRENT_SETTINGS["inject_magic"] = not CURRENT_SETTINGS["inject_magic"]
        if CURRENT_SETTINGS["inject_magic"]:
            print("Magic injection on.")
        else:
            # todo: tee tästä funktio ja ylipäänsä muut tässä filessä
            msg = (
                "Magic injection off. Already injected variables remain in"
                " global/local scopes but won't update."
            )
            print(msg)
        return "continue-in-repl"
    elif user_input in ("!i", "!info"):
        print("\n".join(get_status(frame, event, arg)))
        return "continue-in-repl"
    elif user_input in ("!w", "!where"):
        print_source_lines(frame)
        return "continue-in-repl"
    elif user_input in ("!u", "!up"):
        up()
        return "continue-in-repl"
    elif user_input in ("!d", "!down"):
        down()
        return "continue-in-repl"
    elif user_input in ("!f", "!frame"):
        add_frame(frame)
        return "continue-in-repl"

    elif user_input.startswith("!g") or user_input.startswith("!goto"):
        # must use startswith since argument is expected
        do_goto(frame, original_input)
        return "continue-in-repl"
    elif user_input.startswith("!c") or user_input.startswith("!condition"):
        if CURRENT_SETTINGS["callstack_escape_level"] != 0:
            CURRENT_SETTINGS["callstack_escape_level"] = 0
            print("Resetting escape level to 0 before setting condition.")
        returnvalue = step_condition(original_input)
        return returnvalue
    elif user_input.startswith("!p") or user_input.startswith("!pickle"):
        pickle_object(frame, original_input)
        return "continue-in-repl"
    elif user_input.startswith("!l") or user_input.startswith("!load"):
        unpickle_object(frame, original_input)
        return "continue-in-repl"
    elif user_input.startswith("!e") or user_input.startswith("!echo"):
        echo_previous(original_input)
        return "continue-in-repl"

    else:
        # got a bang that doesnt match anything known
        if original_input.startswith("!"):
            print(f"Invalid bang {repr(original_input)}")
            return "continue-in-repl"
        else:  # got code
            pass


def print_tb(frame, num_frames_to_hide):
    """
    if exception occurs in seapie, num frames tells how many seapie
    relatd frames to hide from the traceback found in exception.
    this is joined with other frames found with tb.extact_stack to show
    all frames from original source and frames from input but not seape itself
    """
    exc_type, exc_val, exc_tb = sys.exc_info()  # Get the traceback

    # if (exc_type, exc_val, exc_tb) == (None, None, None):
    #    # print_tb was called when there is no exception, use stack instead.
    #    # all frames can be found here when there is not exception going on.
    #    tb_frames = traceback.extract_stack()
    # else:
    #    # Extract the traceback frames from the exception object because
    #    # there is an exception going on and we need all frames available
    #    tb_frames = traceback.extract_tb(exc_tb)

    # need to use extract stack to include all frames in stack
    # tb_frames = traceback.extract_stack()

    traceback_exc = traceback.TracebackException(*sys.exc_info())

    # seapie would be present here so we hide it from the middle of the stack
    # Exclude the frames occupied by the debugger
    # if num_frames_to_hide == 0:
    #    # manual check needed because [:-0] is empty list instead of full
    #    tb_exc_stack_filtered = traceback_exc.stack
    # else:
    tb_exc_stack_filtered = traceback_exc.stack[num_frames_to_hide:]

    # we have to use both traceback.extract_stack(frame) and
    # traceback_exc.stack
    # because otherwise frames created in seapie repl would not be visible
    # or frames created in original source would not be visible
    tb_frames = traceback.extract_stack(frame) + tb_exc_stack_filtered

    # Format the filtered traceback
    formatted_traceback = "".join(traceback.format_list(tb_frames))

    print("Traceback (most recent call last):")  # Print header.
    print(formatted_traceback, end="")  # Print traceback,

    # Only print the error itself if an exception is being handled
    if exc_type is not None and exc_val is not None:
        print(f"{exc_type.__name__}: {exc_val}")


def print_source_lines(frame):
    """Reponds to term size

    it might be possible to make this fail?
    """
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

    current_lineno = frame.f_lineno
    filename = frame.f_globals.get("__file__")  # Null check with .get

    if filename is None:
        print("Unable to retrieve the current filename.")
        return

    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except OSError as e:
        print(f"Error opening file: {e}")
        return

    invert_color = "\x1b[7m"
    reset_color = "\x1b[0m"

    max_lineno_width = len(str(len(lines)))
    if max_lineno_width < 6:
        max_lineno_width = 6  # the string ' Next' is 5 character

    for lineno, line in enumerate(lines, start=1):
        line = line[:-1]  # Remove trailing newline with -1
        linenum = str(lineno).rjust(max_lineno_width)  # right aling lineno
        if abs(lineno - current_lineno) <= 10:  # show +- 10 lines.
            if lineno != current_lineno:
                out = f"{linenum} {line}"
            else:
                out = f"{invert_color}{' Next '.rjust(max_lineno_width)}{reset_color} {line}"
            # invert color and reset color lenghts are added to width since
            # they are invisible and dont actually take up space
            out = out[:width]

            print(out)


def up():
    CURRENT_SETTINGS["callstack_escape_level"] += 1
    print(
        "Setting escape level to"
        f" {CURRENT_SETTINGS['callstack_escape_level']}."
        " Check status bar for current frame of this prompt."
    )


def down():
    if CURRENT_SETTINGS["callstack_escape_level"] <= 0:
        CURRENT_SETTINGS["callstack_escape_level"] = 0
        print("Can't do deeper in callstack. Resetting escape level to 0.")
    else:
        CURRENT_SETTINGS["callstack_escape_level"] -= 1
        print(
            "Setting escape level to"
            f" {CURRENT_SETTINGS['callstack_escape_level']}."
            " Check status bar for current frame of this prompt."
        )


def add_frame(frame):
    """Add reference to base frame globals. The frame added is the one
    currently operated on by interpeter."""
    frame_to_add = frame
    global_frame = frame
    while global_frame.f_back is not None:
        global_frame = global_frame.f_back
    module_globals = global_frame.f_globals
    module_globals["FRAME"] = frame_to_add
    print(
        "Added global variable 'FRAME' to root frame. The FRAME refers to"
        f" {repr(frame.f_code.co_name)} frame {repr(frame)}. Remember to"
        " delete the reference with 'del FRAME' to avoid circular references"
        " or memory leaks when you are done with the frame. Use !up to go to"
        " root frame and !down to get back where you were."
    )


def do_goto(frame, user_input):
    """Wohoo. goto in python."""
    command_parts = user_input.split(" ")
    if command_parts[0].lower() not in ("!g", "!goto"):
        print(f"Invalid bang {user_input}")
        return
    if len(command_parts) == 2:
        line_number_str = command_parts[1]
        if line_number_str.isdigit():
            line_number = int(line_number_str)
        else:
            print("Invalid line number. Use: !g 123 or !goto 123")
            return
    else:
        print("Invalid line number. Use: !g 123 or !goto 123")
        return

    try:
        frame.f_lineno = line_number
    except Exception as e:
        print("Goto failed:", str(e))
        return
    else:
        print("Goto succeeded. Next line to execute is", line_number)
        return


def step_condition(user_input):
    command_parts = user_input.split(" ", 1)
    if command_parts[0].lower() not in ("!c", "!condition"):
        print(f"Invalid bang {user_input}")
        return "continue-in-repl"
    if len(command_parts) == 2:
        user_expression = command_parts[1]
        try:
            eval(user_expression)
        except SyntaxError:
            print("SyntaxError. Ignoring the step condition.")
            return "continue-in-repl"
        # Ignore all other errors. We only warn for syntax error.
        except Exception:
            pass

        CURRENT_SETTINGS["step_until_expression"] = user_expression
        print(
            f"Stepping until 'bool(eval({repr(user_expression)}))' is True in"
            " active frame. All errors are ignored."
        )
        return "step-with-repl"
    else:
        print("Missing expression. Use: !c x==0 or !condition x==0")
        return "continue-in-repl"


def echo_previous(user_input):
    command_parts = user_input.split(" ")
    if command_parts[0].lower() not in ("!e", "!echo"):
        print(f"Invalid bang {user_input}")
        return
    if len(command_parts) == 2:
        echo_count_str = command_parts[1]
        if echo_count_str.isdigit():
            echo_count = int(echo_count_str)
        else:
            print("Invalid echo count. Use: !e 3 or !echo 3")
            return
    else:
        print("Invalid echo count. Use: !e 3 or !echo 3")
        return

    CURRENT_SETTINGS["echo_count"] = echo_count
    print("Repeating previous bang", echo_count, "times.")


def pickle_object(frame, user_input):
    """Pickles a Python object and saves it in the 'pickles' subdirectory with
    the rightmost part of the name as the file name.
    This function assumes read-write access was already checked for and that
    the directory was initialized.

    dokumentoi mitä tekee nimille ja että nimet joissa . toimii myös
    """
    command_parts = user_input.split(" ", 1)
    if command_parts[0].lower() not in ("!p", "!pickle"):
        print(f"Invalid bang {user_input}")
        return
    if len(command_parts) == 2:
        obj_name = command_parts[1]
    else:
        print("Missing object name. Use: !p my_object or !pickle my_object")
        return

    file_name = f"{obj_name.split('.')[-1]}"

    pickles_dir = os.path.join(os.path.expanduser("~"), ".seapie", "pickles")

    file_path = os.path.join(pickles_dir, file_name)

    for part in obj_name.split("."):  # Allow dots in name by splitting.
        if not part.isidentifier():
            print(
                f"{repr(obj_name)} is not a valid identifier. Do not use"
                ' literals like "!p \'hello\'" or calls like "!p print()".'
                ' Use "!p hello" or "!p print" instead to refer to an object.'
            )
            return

    try:
        object_ref = eval(obj_name, frame.f_globals, frame.f_locals)
    except Exception as e:
        print(f"Error evaluating object {repr(obj_name)}: {e}")
        return

    try:
        with open(file_path, "wb") as file:
            pickle.dump(object_ref, file, protocol=4)
    except Exception as e:
        print(f"Error pickling object {repr(obj_name)}: {e}")
        return

    print(f"Object {repr(obj_name)} pickled and saved as {repr(file_path)}.")


def unpickle_object(frame, user_input):
    """Loads a pickle file and returns the object and creation date."""

    command_parts = user_input.split(" ", 1)
    if command_parts[0].lower() not in ("!l", "!load"):
        print(f"Invalid bang {user_input}")
        return
    if len(command_parts) == 2:
        object_name = command_parts[1]
    else:
        print("Missing object name. Use: !l objectname or !load objectname")
        print()
        print_pickles()
        print()
        return

    file_name = f"{object_name.split('.')[-1]}"
    pickles_dir = os.path.join(os.path.expanduser("~"), ".seapie", "pickles")
    file_path = os.path.join(pickles_dir, file_name)

    if not object_name.isidentifier():
        print(f"{repr(object_name)} is not a valid identifier.")
        return

    try:
        with open(file_path, "rb") as file:
            object_ref = pickle.load(file)
    except Exception as e:
        print(f"Error loading pickle file {repr(file_path)}: {e}")
        return

    frame.f_locals[object_name] = object_ref

    print(f"{repr(object_name)} loaded into active frame from {repr(file_path)}.")


def print_help():
    print("nice")
