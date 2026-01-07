"""Core REPL loop and input handling for seapie debugger.

Entry point: loop() is installed as the trace/profile func via sys.settrace/setprofile.

STATE is a module-level dict rather than a class at least for now. Debugging is often
singleton by nature; there's one trace hook, one terminal, one user, one session. Class
would just be a singleton in this case. If future versions of seapie support multiple
simultaneous sessions for different threads, a class would be needed.

The STATE dict is accessed across modules:
    - commands.py: do_* handlers read/write flags (pretty, verbose, keep_expression)
    - helpers.py: SIGINT handling, walk condition management, displayhook
    - repl.py: loop() orchestrates everything using STATE
"""

import codeop
import ctypes
import sys
import types

import seapie.commands
import seapie.constants
import seapie.helpers

STATE = {
    "walk_condition": None,     # Expression that must be True to stop walking
    "keep_expression": None,    # Expression to evaluate and display at top of terminal
    "pretty": True,             # Prettyprint output with pprint
    "verbose": True,            # Show "stopped at" messages after any stepping
    "first_walk_done": False,   # Track if we've shown the first-walk tip
    "walk_interrupted": False,  # Flag set by SIGINT handler during walks
    "original_sigint": None,    # Saved SIGINT handler to restore after walk
    "original_frame": None,     # Frame where debugger stopped (for !frame home)
    "working_frame": None,      # Current frame being inspected (sometimes != original)
    "event": None,              # Current trace event type (call/line/return/exception)
    "signal": "continue",       # Control flow signal: continue/walk/detach
}


def get_user_input():
    """Reads a (multiline) input like Python interpreter does.

    Returns '!command' or compiled code.
    """
    # Exit without showing prompt if interpreter is in process of closing
    if sys.stdin.closed:
        exit()  # Avoid 'stdin is closed' error loop if interpreter is closing

    def read_multiline_input_or_command():
        lines = []
        while True:  # read input until it is completed or fails or we get a command
            prompt_text = ">>> " if not lines else "... "
            lines.append(input(prompt_text))
            if lines[0].startswith("!"):  # Got a command on first line.
                return lines[0]
            compiled = codeop.compile_command("\n".join(lines), "<seapie>", "single")
            if compiled:
                return compiled  # Compilation returns None if given start of ok code.

    try:
        return read_multiline_input_or_command()
    except EOFError:  # Mimic EOF behaviour from ctrl+d by user in input.
        print()  # Print newline before exit because ctrl+d cancels the input
        exit()
    except KeyboardInterrupt:  # Ctrl+c by user in input
        print()  # Print newline before traceback because ctrl+c cancels the input
        # 3 hides: [0]=show_tb, [1]=get_user_input, [2]=loop
        seapie.helpers.show_tb(frames_to_hide=3, repl_tb=False)
        return None  # Signal main loop to redraw !keep and continue
    except (SyntaxError, ValueError, OverflowError, UnicodeDecodeError):  # Compile fail
        # 3 hides: [0]=show_tb, [1]=get_user_input, [2]=loop
        seapie.helpers.show_tb(frames_to_hide=3, repl_tb=False)
        return None  # Signal main loop to redraw !keep and continue

def handle_user_input_exec(user_input):
    """Execute user code in the working frame's context."""
    frame = STATE["working_frame"]
    try:  # Try to exec user input if codetype was successfully returned from input
        exec(user_input, frame.f_globals, frame.f_locals)
        try:
            # exec() modifies frame.f_locals dict, but CPython uses a separate 'fast
            # locals' array for actual variable access. PyFrame_LocalsToFast copies
            # f_locals back to fast locals, making assignments like "x = 1" in the REPL
            # persist in the frame. The second arg (1) means "clear" - also remove
            # variables deleted from f_locals.
            c_one = ctypes.c_int(1)
            ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), c_one)
        except (AttributeError, OSError, TypeError):  # Not available outside CPython
            if not hasattr(handle_user_input_exec, "warning_given"):
                print("Can't update locals variables. Are you using CPython?")
                handle_user_input_exec.warning_given = True
    # Exception handling philosophy: errors from user-provided code should be displayed
    # as tracebacks, not propagate up and crash the debugger; we are mimicking the
    # interpreter. Only system-critical errors (MemoryError, SystemExit) are reraised.
    # KeyboardInterrupt from user code is treated as an error to display (Ctrl+C during
    # input is handled separately in get_user_input).
    except (MemoryError, SystemExit):
        raise
    except BaseException:
        # 3 hides: [0]=show_tb, [1]=handle_user_input_exec, [2]=loop
        seapie.helpers.show_tb(frames_to_hide=3, repl_tb=True)
    STATE["signal"] = "continue"

def handle_user_input_command(user_input):
    """Handle a !command. Sets STATE["signal"] to control repl flow.

    signal values:
        - "continue": continue the repl loop in current working frame
        - "walk": walk condition set in STATE, step (exit repl, return loop)
        - "detach": detach debugger and resume execution (exit repl, return None)
    """
    # Get command name and arguments
    parts = user_input[1:].split()
    cmd_name = parts[0] if parts else ""

    cmd = seapie.commands.get_command(cmd_name)
    if cmd is None:
        quicklist = seapie.constants.HELP_QUICKLIST[:-1]  # Drop newline with -1
        print(f"{seapie.constants.SKULL}  Unknown command !{cmd_name}\n{quicklist}")
        STATE["signal"] = "continue"
        return
    handler, arg_count, requires_top_frame = cmd

    # Parse arguments: "1+" means rest of line is a single expression argument
    if arg_count == "1+":
        # Everything after "!cmd " is a single argument (for expressions with spaces)
        rest = user_input[1 + len(cmd_name):].strip()
        cmd_args = [rest] if rest else []
        valid = len(cmd_args) >= 1
    else:
        cmd_args = parts[1:]
        valid = len(cmd_args) == arg_count

    if not valid:
        help_text = seapie.commands.get_command_help(cmd_name)[:-1]  # Drop last newline
        arg = "argument" if arg_count == 1 else "arguments"
        arg_inf = f"{arg_count} {arg}"
        print(f"{seapie.constants.SKULL}  Expected {arg_inf}, got {len(cmd_args)}")
        print(f"Usage:\n{help_text}")
        STATE["signal"] = "continue"
        return

    # Auto-return to top frame for stepping commands
    if requires_top_frame and STATE["working_frame"] is not STATE["original_frame"]:
        STATE["working_frame"] = STATE["original_frame"]
        print(f"{seapie.constants.HOME}  Returned to home frame to allow stepping")

    # Execute command handler. All have signature: (args) -> None, sets STATE["signal"]
    # Only keyboard interrupt is handled here, other exceptions are allowed to crash
    # seapie to reveal bugs if present in handlers.
    try:
        handler(cmd_args)
    except KeyboardInterrupt:
        print(f"\n{seapie.constants.STOP}  Command interrupted")
        STATE["signal"] = "continue"


def loop(frame, event, arg):
    """REPL that gets called on each trace event.

    'frame' is the trace frame, stored as both original_frame and working_frame.
    working_frame can be changed by !frame commands during the REPL loop.
    """
    # Skip events/frames that shouldn't be traced by seapie
    if not seapie.helpers.is_traceable(frame, event):
        return None

    # Store frame, working frame, and event into state
    STATE["original_frame"] = frame  # Store home frame in case user moves in stack
    STATE["working_frame"] = frame   # Store the current frame being inspected in repl
    STATE["event"] = event           # Store for handlers that need it

    # Update magic variables and check walk condition (walk condition checks SIGINT)
    seapie.helpers.update_magic_variables(frame, event, arg)
    if seapie.helpers.check_walk_condition() == "keep_walking":
        return loop

    # This is the main REPL loop that gets called on each trace event
    while True:

        # Update !keep expression if given before blocking at getting user input
        seapie.helpers.show_keep_value()
        user_input = get_user_input()

        # Handle user input
        if type(user_input) is types.CodeType:
            handle_user_input_exec(user_input)
        elif type(user_input) is str:
            handle_user_input_command(user_input)
        else:
            continue  # user input failed, continue loop to retry

        # Check signal set by handle_user_input_exec or handle_user_input_command
        if STATE["signal"] == "walk":
            return loop
        if STATE["signal"] == "detach":
            return None
