"""
bang handler stuff and related tools

"""

import os
import pickle
import sys
import traceback

from .state import STATE
from .status import get_status, print_pickles


def bang_handler(user_input, frame, event, arg):
    """Attempts to do complete adnlings of bands. returns values only

    if the enclosing repl must take an action that cant be done here.

    dokumentoi tai poista aliakset

    possible actions and return values:
    * exit() happens
    * step-with-repl; repl should return itself as the new trace func

    input is case sensitive because !condition has to be case sensitive


    returns true if the code should step
    false if code should not step

    all the do functions cause side effects.
    """
    original_input = user_input  # needed as arg for bangs that take args
    user_input = user_input.lower()

    if original_input.startswith("!"):  # save the bang
        if user_input.startswith("!e") or user_input.startswith("!echo"):
            pass  # echo bang is not saved to avoid infinite loop
        else:
            STATE["previous_bang"] = original_input

    # These bangs do not contain arguments so using simple check is ok.
    if user_input in ("!q", "!quit"):
        return do_quit()
    elif user_input in ("!r", "!run"):
        return do_run(frame)
    elif user_input in ("!h", "!help"):
        return do_help()
    elif user_input in ("!t", "!traceback"):
        return do_tb(frame, frames_to_hide=0)  # No exception, nothing to hide.
    elif user_input in ("!b", "!bar"):
        return do_bar()
    elif user_input in ("!m", "!magic"):
        return do_magic()
    elif user_input in ("!i", "!info"):
        return do_info(frame, event, arg)
    elif user_input in ("!w", "!where"):
        return do_where(frame)
    elif user_input in ("!u", "!up"):
        return do_up()
    elif user_input in ("!d", "!down"):
        return do_down()
    elif user_input in ("!f", "!frame"):
        return do_frame(frame)

    # These bangs contain arguments so must use startswith.
    elif user_input.startswith("!g") or user_input.startswith("!goto"):
        return do_goto(frame, original_input)
    elif user_input.startswith("!s") or user_input.startswith("!step"):
        return do_step(original_input)
    elif user_input.startswith("!p") or user_input.startswith("!pickle"):
        return do_picle(frame, original_input)
    elif user_input.startswith("!l") or user_input.startswith("!load"):
        return do_unpickle(frame, original_input)
    elif user_input.startswith("!e") or user_input.startswith("!echo"):
        return do_echo(original_input)

    else:
        return do_invalid(original_input)  # Got an invalid bang.


def do_tb(frame, frames_to_hide):
    """
    if exception occurs in seapie, frames_to_hide tells how many seapie
    relatd frames to hide from the traceback found in exception.
    this is joined with other frames found with tb.extact_stack to show
    all frames from original source and frames from input but not seape itself
    """

    traceback_exc = traceback.TracebackException(*sys.exc_info())

    # seapie would be present here so we hide it from the middle of the stack
    # Exclude the frames occupied by the debugger
    tb_exc_stack_filtered = traceback_exc.stack[frames_to_hide:]

    # we have to use both traceback.extract_stack(frame) and
    # traceback_exc.stack
    # because otherwise frames created in seapie repl would not be visible
    # or frames created in original source would not be visible
    tb_frames = traceback.extract_stack(frame) + tb_exc_stack_filtered

    # Format the filtered traceback
    formatted_traceback = "".join(traceback.format_list(tb_frames))

    print("Traceback (most recent call last):")  # Print header.
    print(formatted_traceback, end="")  # Print traceback,

    exc_type, exc_val, _exc_tb = sys.exc_info()  # Get active exception if any.
    if exc_type is not None and exc_val is not None:  # Print active exception.
        print(f"{exc_type.__name__}: {exc_val}")

    return False


def do_frame(frame):
    """Add reference to base frame globals. The frame added is the one
    currently operated on by interpeter."""
    frame.f_locals["__frame__"] = frame
    print(
        "Added local variable __frame__ to current frame. Remember to delete"
        " the reference with 'del __frame__' when you are done with the frame"
        " to avoid circular references or memory leaks."
    )
    return False


def do_goto(frame, user_input):
    """Wohoo. goto in python."""
    command_parts = user_input.split(" ")
    if command_parts[0].lower() not in ("!g", "!goto"):
        print(f"Invalid bang {user_input}")
        return False
    if len(command_parts) == 2:
        line_number_str = command_parts[1]
        if line_number_str.isdigit():
            line_number = int(line_number_str)
        else:
            print("Invalid line number. Use: !g 123 or !goto 123")
            return False
    else:
        print("Invalid line number. Use: !g 123 or !goto 123")
        return False

    try:
        frame.f_lineno = line_number
    except Exception as e:
        print("Goto failed:", str(e))
        return False
    else:
        print("Goto succeeded. Next line to execute is", line_number)
        return False


def do_step(user_input):
    command_parts = user_input.split(" ", 1)

    if command_parts[0].lower() not in ("!s", "!step"):
        print(f"Invalid bang {user_input}")
        return False

    if len(command_parts) == 1:  # simple step
        return True
    elif len(command_parts) == 2:  # step with a condition
        user_expression = command_parts[1]
        try:
            eval(user_expression)
        except SyntaxError:
            print("SyntaxError. Ignoring the step condition.")
            return False
        # Ignore all other errors. We only warn for syntax error.
        except Exception:
            pass

        # reset lvl
        if STATE["callstack_escape_level"] != 0:
            STATE["callstack_escape_level"] = 0
            print("Resetting escape level to 0 before stepping.")

        STATE["step_until_expression"] = user_expression
        print(
            f"Stepping until 'bool(eval({repr(user_expression)}))' is True in"
            " active frame. All errors are ignored."
        )
        return True


def do_echo(user_input):
    command_parts = user_input.split(" ")
    if command_parts[0].lower() not in ("!e", "!echo"):
        print(f"Invalid bang {user_input}")
        return False
    if len(command_parts) == 2:
        echo_count_str = command_parts[1]
        if echo_count_str.isdigit():
            echo_count = int(echo_count_str)
        else:
            print("Invalid echo count. Use: !e 3 or !echo 3")
            return False
    else:
        print("Invalid echo count. Use: !e 3 or !echo 3")
        return False
    STATE["echo_count"] = echo_count
    print("Repeating previous bang", echo_count, "times.")


def do_picle(frame, user_input):
    """Pickles a Python object and saves it in the 'pickles' subdirectory with
    the rightmost part of the name as the file name.
    This function assumes read-write access was already checked for and that
    the directory was initialized.

    dokumentoi mitä tekee nimille ja että nimet joissa . toimii myös
    """
    command_parts = user_input.split(" ", 1)
    if command_parts[0].lower() not in ("!p", "!pickle"):
        print(f"Invalid bang {user_input}")
        return False
    if len(command_parts) == 2:
        obj_name = command_parts[1]
    else:
        print("Missing object name. Use: !p my_object or !pickle my_object")
        return False

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
            return False

    try:
        object_ref = eval(obj_name, frame.f_globals, frame.f_locals)
    except Exception as e:
        print(f"Error evaluating object {repr(obj_name)}: {e}")
        return False

    try:
        with open(file_path, "wb") as file:
            pickle.dump(object_ref, file, protocol=4)
    except Exception as e:
        print(f"Error pickling object {repr(obj_name)}: {e}")
        return False

    print(f"Object {repr(obj_name)} pickled and saved as {repr(file_path)}.")
    return False


def do_unpickle(frame, user_input):
    """Loads a pickle file and returns the object and creation date."""

    command_parts = user_input.split(" ", 1)
    if command_parts[0].lower() not in ("!l", "!load"):
        print(f"Invalid bang {user_input}")
        return False
    if len(command_parts) == 2:
        obj_name = command_parts[1]
    else:
        print("Missing object name. Use: !l objectname or !load objectname")
        print()
        print_pickles()
        print()
        return False

    file_name = f"{obj_name.split('.')[-1]}"
    pickles_dir = os.path.join(os.path.expanduser("~"), ".seapie", "pickles")
    file_path = os.path.join(pickles_dir, file_name)

    if not obj_name.isidentifier():
        print(f"{repr(obj_name)} is not a valid identifier.")
        return False

    try:
        with open(file_path, "rb") as file:
            object_ref = pickle.load(file)
    except Exception as e:
        print(f"Error loading pickle file {repr(file_path)}: {e}")
        return False

    frame.f_locals[obj_name] = object_ref

    print(f"{repr(obj_name)} loaded into active frame from {repr(file_path)}.")
    return False


def do_help():
    print("nice")
    return False


def do_magic():
    STATE["inject_magic"] = not STATE["inject_magic"]
    if STATE["inject_magic"]:
        print("Magic injection on.")
    else:
        # todo: tee tästä funktio ja ylipäänsä muut tässä filessä
        msg = (
            "Magic injection off. Already injected variables remain in"
            " global/local scopes but won't update."
        )
        print(msg)
    return False


def do_quit():
    exit()


def do_run(frame):
    """Returning the"""
    frame.f_trace = None
    sys.settrace(None)
    return True


def do_bar():
    STATE["show_bar"] = not STATE["show_bar"]
    if STATE["show_bar"]:
        print("Bar on.")
    else:
        print("Bar off.")
    return False


def do_info(frame, event, arg):
    print("\n".join(get_status(frame, event, arg)))
    return False


def do_where(frame):
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
        return False

    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except OSError as e:
        print(f"Error opening file: {e}")
        return False

    invert_color = "\x1b[7m"
    reset_color = "\x1b[0m"

    max_lineno_width = len(str(len(lines)))
    if max_lineno_width < 6:
        max_lineno_width = 6  # the string ' Next ' is 6 character

    for lineno, line in enumerate(lines, start=1):
        line = line[:-1]  # Remove trailing newline with -1
        linenum = str(lineno).rjust(max_lineno_width)  # right aling lineno
        if abs(lineno - current_lineno) <= 10:  # show +- 10 lines.
            if lineno != current_lineno:
                out = f"{linenum} {line}"
            else:
                out = (
                    f"{invert_color}{' Next '.rjust(max_lineno_width)}"
                    f"{reset_color} {line}"
                )
            # invert color and reset color lenghts are added to width since
            # they are invisible and dont actually take up space
            out = out[:width]

            print(out)
    return False


def do_up():
    STATE["callstack_escape_level"] += 1
    print(
        "Setting escape level to"
        f" {STATE['callstack_escape_level']}."
        " Check status bar to see in which frame you are."
    )
    return False


def do_down():
    if STATE["callstack_escape_level"] <= 0:
        STATE["callstack_escape_level"] = 0
        print("Can't do deeper in callstack. Resetting escape level to 0.")
    else:
        STATE["callstack_escape_level"] -= 1
        print(
            "Setting escape level to"
            f" {STATE['callstack_escape_level']}."
            " Check status bar for current frame of this prompt."
        )
    return False


def do_invalid(original_input):
    print(f"Invalid bang {repr(original_input)}")
    return False
