#!/usr/bin/env python3

"""the only function you should use from here is prompt.

there is global state and everything is monolitchic to simplify the structure
of the debugger; the amount of argument passing is reduced and there is no
need for a class. The top priority was to simlify prompt() and repl_loop()

dokumentoi mihin tarkoitukseen seapie directory on
"""

import codeop
import inspect
import sys

import seapie.handlers
import seapie.helpers


def set_trace():
    """
    essentially equivalent of pdb.set_trace function.  set traceto repl_loop.

    starts traving if trace func is none. if trace func is repl_llop
    this call does nothing. if trace func is something else raise.
    """
    if sys.gettrace() is None:
        try:
            import readline  # noqa # readline (if available) needed for line editing.
        finally:
            seapie.helpers.show_banner()
            inspect.currentframe().f_back.f_trace = repl
            sys.settrace(repl)



def get_repl_input():
    """Fake python repl until we can return code as string or a bang.
    the code could cause an error when compiling and then bang might not be
    valid. The functionmight read multiple input() calls for each function call
    to mimic a python interpreter.

    no error handlnig is done here, everything is done in the enclosing repl function
    """

    lines = []
    while True:  # read input until it is completed or fails or we get a bang
        if not sys.stdin.closed:  # Check for closed status to avoid printing prompt unnecessarily when already closed
            #sys.stdin was closed > input fail > python is closing > exit().
            lines.append(input(">>> " if not lines else "... "))
        else:
            exit()

        if lines[0].startswith("!"):  # Got a bang on first line.
            return lines[0]

        compiled = codeop.compile_command("\n".join(lines), "<seapie>", "single")
        if compiled:  # "compiled" is None if "lines" was start of valid code.
            return compiled



def repl(frame, event, arg):
    """args: frame, event, arg

    read-evaluate-print-loop that gets called when tracing code. this
    basically gets run between evey line

    under the hood the return value is ignored or used to set
    local trace function depending on the event.

    the input and exec both have their own error handling so this main loop
    does not need error handling

    bang handlers can make changes to this frame or change it for another frame.
    """

    # Skip tracing certain frames.
    if hasattr(sys, "last_exc") or frame.f_code in (exit.__call__.__code__, set_trace.__code__):
        return  # Don't trace uncaught error process, exit() process, or own breakpoint.

    while True:  # This is the main repl (>>> ... ... ...) loop. It's triggered between every line of source code
        seapie.helpers.inject_magic_vars(frame, event, arg)
        try:
            with seapie.helpers.handle_input_exceptions(frame):
                user_input = get_repl_input()  # input is either code or bang
            with seapie.helpers.handle_exec_exceptions(frame):
                seapie.handlers.handle_input(frame, event, arg, user_input) # handlers might return a new working frame or they might raise Step. in case of raise, a f is not updated
        except seapie.helpers.Step:  # Got step signal from input or handle input
            return repl  # Steps code forward. no continue was raised.
        except seapie.helpers.Continue:  # Got continue signal from input or handle input
            continue  # keep in current repl loop, dont step code.


