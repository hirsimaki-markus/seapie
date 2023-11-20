#!/usr/bin/env python3

"""the only function you should use from here is prompt.

there is global state and everything is monolitchic to simplify the structure
of the debugger; the amount of argument passing is reduced and there is no
need for a class. The top priority was to simlify prompt() and repl_loop()

dokumentoi mihin tarkoitukseen seapie directory on
"""

import codeop
import ctypes
import inspect
import sys

from .bang import bang_handler, do_tb
from .helpers import (
    escape_frame,
    init_seapie_dir_and_reset_state,
    print_start_banner,
    step_until_condition,
    update_magic_vars,
)
from .state import STATE
from .status import update_status_bar


def get_repl_input(frame):
    """Fake python repl until we can return code as string or a bang.
    the code could cause an error when compiling and then bang might not be
    valid. The functionmight read multiple input() calls for each function call
    to mimic a python interpreter.

    frame is required as argument to correcly print traceback if needed

    this function prints tracebacks instead of raising to make repl loop
    cleaner

    this function never raises and always returns a string, any erros are
    handled in this functon such that traceback is printed.
    """

    # Check if previous bang should be echoed instead of reading te user input.
    if STATE["echo_count"] > 0:
        STATE["echo_count"] -= 1
        return STATE["previous_bang"]

    try:  # readline (when available) is needed for input line editing.
        import readline  # noqa: F401  # Ignore unused import in flake8.
    except ImportError:
        pass

    lines = []
    while True:  # read input until it is completed or fails or we get a bang
        try:
            line = input(">>> " if not lines else "... ")
        except KeyboardInterrupt:  # ctrl + c
            print("\nKeyboardInterrupt")
            lines = []
            continue
        except EOFError:  # ctrl + d / ctrl + z
            print()
            exit()
        except ValueError:  # sys.stdin.close() was likely called during exit.
            print()
            exit()
        if line.startswith("!") and not lines:  # Got a bang on first line.
            return line
        lines.append(line)
        try:
            entry = "\n".join(lines)
            if codeop.compile_command(entry, "<seapie>", "single") is not None:
                return entry
        except (SyntaxError, ValueError, OverflowError):  # Retry on error.
            # Hiding these 4 frames: "repl_input", "codeop.compile_command",
            # "codeop._maybe_compile", "codeop._compile.
            do_tb(frame, frames_to_hide=4)
            lines = []
            continue


def true_exec(code, scope):
    """This function is provided for backwards compability with earlier seapie
    versions. It might be deprecated later.
    """
    frame = sys._getframe(scope + 1)  # +1 escapes true_exec itself
    exec(code, frame.f_globals, frame.f_locals)

    # PyFrame_LocalsToFast allows overwriting vars (like functions) in source.
    c_int1 = ctypes.c_int(1)  # 1 is for delete and 0 is for update only.
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), c_int1)


def repl_exec(frame, source):
    """str representing python sauce. and compiles it. assume that the code is

    performs exec in arbitrary frame and attempts to modify its state like
    interactive interpreter would
    """
    try:
        # Compile code first to allow showing "Ellipsis" for "..." input etc.
        compiled_code = codeop.compile_command(source, "<seapie>", "single")
        exec(compiled_code, frame.f_globals, frame.f_locals)
    except SystemExit:  # Separate exit before catching base exception.
        exit()
    except BaseException:
        do_tb(frame, frames_to_hide=2)  # Hide "repl-exec" & "<seapie>" of exec

    # PyFrame_LocalsToFast allows overwriting vars (like functions) in source.
    c_int1 = ctypes.c_int(1)  # 1 is for delete and 0 is for update only.
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), c_int1)


def repl_loop(frame, event, arg):
    """read-evaluate-print-loop that gets called when tracing code. this
    basically gets run between evey line

    if returning something else than none, always returns repl_loop itself so
    it will be used for both local and global trace func


    under the hood the return value is ignored or used to set
    local trace function depending on the event.

    the input and exec both have their own error handling so this main loop
    does not need error handling

    this function is essentially called between every source line

    most parts of this function use the global state.
    """

    if hasattr(sys, "last_exc"):  # Unhandled error in original source.
        return  # Don't return trace func to not trace Python's error handling.

    # Dont trace new prompt calls. uses magic string in docstring.
    if "do-not-modify-this-string-it-is-used-by-seapie" in (
        frame.f_code.co_consts[0] or ""  # null check with or ""
    ):
        return  # Not returning a local trace function to skip seapie's frame.

    if frame.f_locals.get("self") is exit:
        # Dont trace intrnal exit handling. exit note: Exit is class.
        return  # Not returning a local trace function to skip exit's frames.

    while True:  # This is the main repl (>>> ... ... ...) loop.
        current_frame = escape_frame(frame)  # Escape frame based on STATE.

        update_magic_vars(current_frame, event, arg)  # Uses STATE.
        update_status_bar(current_frame, event, arg)  # Uses STATE.

        if step_until_condition(frame):  # Note: frame, not current_frame.
            return repl_loop

        if (user_input := get_repl_input(current_frame)).startswith("!"):
            if bang_handler(user_input, current_frame, event, arg):
                return repl_loop
            continue

        repl_exec(current_frame, user_input)  # All guard clauses passed; exec.


def prompt():
    """
    essentially set_trace function.  set traceto repl_loop.

    starts traving if trace func is none. if trace func is repl_llop
    this call does nothing. if trace func is something else raise.

    if not tracing:
       banner,
       init,
       Set trace function for active frame and then for all future frames.

    note: modifying this function is risky. repl_loop relies on there being
    only 1 variable with a specific name. thi is used to identify if tracing
    should be skipped so that seapie does not trace itself.

    note that this function does not assign any variables except for the hidden
    one.

    do-not-modify-this-string-it-is-used-by-seapie

    it is essential that this function does not call more functions if trace
    function is already repl_loop

    """
    if (trace := sys.gettrace()) is None:
        print_start_banner()
        init_seapie_dir_and_reset_state()
        inspect.currentframe().f_back.f_trace = repl_loop
        sys.settrace(repl_loop)
    elif trace is repl_loop:
        print("Ignoring call to seapie because seapie is already tracing.")
    else:
        raise RuntimeError(f"Trace function already set: {trace}")
