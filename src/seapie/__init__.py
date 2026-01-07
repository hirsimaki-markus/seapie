"""seapie - Debugger for humans. Get the familiar >>> _ REPL anywhere in your script.

REPL-based debugger that uses sys.settrace/sys.setprofile to intercept Python execution.
The debugger provides a familiar >>> _ prompt where you can inspect and modify state,
navigate the callstack, and step through code with flexible walk conditions.

Usage:
    Test seapie without a script (do this):
        python -c 'import seapie; seapie.breakpoint()'

    In script (do this):
        import seapie
        seapie.breakpoint()  # Open the debugger, primary use case
        seapie.show_help()  # Just view help without using the debugger

    In normal Python REPL (don't do this, undefined behaviour):
        Python 3.13.3 (main, May 27 2025, 12:54:28) [GCC 13.3.0] on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import seapie; seapie.breakpoint()
        !!! seapie behaviour outside of scripts is undefined !!!

Code flow when dropping to breakpoint (the >>> loop() is entered at each trace event):
    seapie.breakpoint() ->
        sys.settrace(loop) ->
            seapie.repl.loop() handles events & code execution ->
                seapie.repl.get_user_input() reads input ->
                    seapie.repl.handle_user_input_command() handles commands ->
                    seapie.repl.handle_user_input_exec() handles code execution ->
"""

from seapie.helpers import breakpoint, show_help  # Convenience imports

# Single source of version number. Uses <major>.<minor>.<patch>. Skip versions with
# trailing/leading zeroes. Lone zeroes (such as in 0.1.0) are ok. When incrementing a
# number, reset other numbers right of it to 0.
__version__ = "4.0.0"
__author__ = "Markus Hirsimäki"
__copyright__ = "This work is dedicated to public domain under The Unlicense."
__license__ = "The Unlicense"
