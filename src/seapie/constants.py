"""Constants used across seapie"""

# Constants only; no imports allowed here to avoid circular imports





# Emoji constants for consistent output
PIE = "🥧"        # Unused
WALK = "🚶"       # Walking code
STEP = "🦶"       # Stepping
UP = "👆"         # Frame up
DOWN = "👇"       # Frame down
HOME = "🏠"       # Frame home
SKULL = "💀"      # Errors/usage
DETACH = "🔌"     # Detaching
ATTACH = "🔗"     # Attaching
PRETTYON = "✨"   # Prettyprint on
PRETTYOFF = "📄"  # Prettyprint off
SLOW = "🐌"       # Tracing mode (slow)
FAST = "⚡"       # Profiling mode (fast)
EYE = "👁️"        # Keep expression
STOP = "⛔"       # Interrupt
JUMP = "🚀"       # Goto jump
MAGIC = "🪄"      # Magic variables





# VT100 escape sequences for color inversion
VT_INV = "\033[7m"
VT_RESET = "\033[0m"

# VT100 escape sequences for cursor control
VT_SAVE = "\033[s"       # Save cursor position
VT_RESTORE = "\033[u"    # Restore cursor position
VT_MOVETOP = "\033[1;1H"  # Move to row 1, column 1
VT_CLEARLINE = "\033[2K"  # Clear entire line

# Box drawing characters
BOX_H = '─'   # Horizontal
BOX_V = '│'   # Vertical
BOX_TL = '┌'  # Top-left corner
BOX_TR = '┐'  # Top-right corner
BOX_BL = '└'  # Bottom-left corner
BOX_BR = '┘'  # Bottom-right corner





# Help documentation
HELP_HEADER = f"{VT_INV} Help navigation: enter / arrows / scroll / q {VT_RESET}\n"

HELP_QUICKSTART = f"""{JUMP} Quickstart
    >>> !step next    Step to next line in current function
    >>> !continue     Stop debugging and resume execution
    >>> !traceback    Show callstack
    >>> !location     Show source context
    >>> _magic_       Show all magic variables at once
"""

HELP_BRIEF = f"""{PIE} Overview
     The >>> prompt from seapie.breakpoint() is a live Python interpreter paused at a
     breakpoint. Expressions and statements execute immediately, updating program state.
     Special !commands and _magic_ variables are available for inspection and stepping.
"""

HELP_QUICKLIST = f"""{FAST} !command quicklist (example: >>> !location)
    !(h)elp           Show this help message
    !(l)ocation       Show source code around currently executing line
    !(t)raceback      Show callstack with current frame highlighted
    !(f)rame          Move up and down in callstack
    !(k)eep           Constantly show any Python expression at the top of the terminal
    !(s)tep           Step through code execution
    !(e)vent          Step until a specific event type
    !(u)ntil          Step until a target like linenumber or file
    !(w)alk           Step until arbitrary expression is True
    !(g)oto           Jump execution to a line in current frame
    !(c)ontinue       Completely detach debugger and resume normal execution
    !(v)erbose        Toggle verbose output from other commands
    !(p)retty         Toggle prettyprinting of the interpreter output
"""

HELP_MAGIC = f"""{MAGIC} Magic variables quicklist (example: >>> _line_)
    These built-in debugger variables are automatically updated every time execution
    is stepped using !step / !event / !walk / !until. They can be used to inspect state
    and as part of expression for !walk. Magic variables do not overwrite local or
    global variables, but may be shadowed by locals or globals with the same name.

    _line_      Current line number about to execute
                example: 43

    _source_    Source code of the current line about to execute
                example: '    final = controller()'

    _path_      Full path to the current source line's file
                example: '/home/user/seapie/test/run_manual_test2.py'

    _return_    Value about to be returned from current function, if at return event
                example: [1, 1, 2, 3, 5, 8, 13]

    _exception_ Exception about to be propagated, if at exception event
                example: ZeroDivisionError('division by zero')

    _event_     Current debug event: 'call', 'line', 'return', or 'exception'
                example: 'call'

    _callstack_ List of function names in the callstack (oldest → newest)
                example: ['<module>', 'main', 'controller', 'get_data']

    _magic_     Convenience dict of all magic variables above
                example: <dict containing all magic variables above>
"""

HELP_COMMAND_REFERENCE_HEAD = f"""{PRETTYOFF} Command reference"""

HELP_HELP = """    !help
    Do seapie.show_help() or !help in debugger session to show this help. Detailed
    descriptions and examples for each command follow.
"""

HELP_LOCATION = """    !location
    Show source code around the currently executing line for the working frame being
    inspected. Using !frame <up/down/home> will update what !location shows.
"""

HELP_TRACEBACK = """    !traceback
    Show callstack with current working frame highlighted. Using !frame <up/down/home>
    will update what !traceback shows. The actual callstack contains more frames than
    what is shown with !traceback as seapie internals are excluded.
"""

HELP_FRAME = """    !frame <up/down/home>
    Move up and down in callstack. 'up' moves to older frames and 'down' moves to newer
    frames. Home returns to the newest frame.
"""

HELP_KEEP = """    !keep <expression>
    Keep an evaluated expression always visible at the top of terminal. Argument is an
    expression. Use !keep None to clear the current keep.
    Examples:
    - !keep _line_                              Show current line number
    - !keep _path_.split('/')[-1], _line_       Show current file and line number
    - !keep _magic_                             Show all magic variables at once
    - !keep "ERROR" if _exception_ else "OK"    Status indicator based on exception
    Example output at top of terminal:
    ┌─────────────────── _path_.split('/')[-1], _line_ ───────────────────┐
    │ ('run_manual_test.py', 20)                                          │
    └─────────────────────────────────────────────────────────────────────┘
"""

HELP_STEP = """    !step <small/into/over/out/line/next/return>
    Step through execution. Supports both IDE-style and pdb-style arguments.
    Use Ctrl+C to interrupt long-running steps. See !event/!until/!walk for more.
    - small           Stop at the next debug event (smallest possible step)
    - into / line     Stop at the next line anywhere (enters functions; pdb's 'step')
    - over / next     Stop at the next line in current frame only (pdb's 'next')
    - out / return    Step out of current function (pdb's 'return')
"""

HELP_EVENT = """    !event <line/call/return/exception>
    Step until a specific event type occurs.
    Use Ctrl+C to interrupt long-running steps. See !step/!until/!walk for more.
    - line         Stop at the next line event
    - call         Stop at the next function call
    - return       Stop at the next function return
    - exception    Stop at the next exception
"""

HELP_UNTIL = """    !until <kind> <target>
    Step until a condition is met. Takes two arguments: <kind> and <target>.
    Use Ctrl+C to interrupt long-running steps. See !step/!event/!walk for more.
    - !until enter <func>          Stop when entering function named <func>
    - !until line <number>         Stop at line <number> in the working frame's file
    - !until source <string>       Stop when current line's source contains <string>
    - !until path <string>         Stop when current line's filepath contains <string>
    - !until exception <string>    Stop when active exception's name contains <string>
    - !until return <string>       Stop when active return's repr() contains <string>
    Examples:
    - !until enter main            Stop when function 'main' is called
    - !until line 42               Stop at line 42 in current file
    - !until source print          Stop when source contains 'print'
    - !until path mymodule         Stop when filepath contains 'mymodule'
    - !until exception Zero        Stop when 'Zero' is part of the exception type name
    - !until return ok             Stop when 'ok' is part of the return value's repr()
"""

HELP_WALK = """    !walk <expression>
    Step until an expression evaluates to True. The expression can reference any
    local, global, or magic variable. If an exception occurs due to the expression,
    the walk stops. !walk is the underlying implementation for !step, !event, !until.
    Use Ctrl+C to interrupt long-running steps. See !step/!until/!event for more.
    Examples:
    - !walk _line_ == 42                          Stop at line 42
    - !walk "x" in locals() and x == 1            Stop when x exists and equals 1
    - !walk 'error' in _source_                   Stop when source contains 'error'
    - !walk _event_ == 'exception'                Stop on any exception
    - !walk len(_callstack_) > 5                  Stop when call depth exceeds 5
    - !walk _line_ > 100 and 'myvar' in _source_  Combine conditions freely
    Advanced examples showing !until and !walk equivalences:
    - !until enter main
      !walk _event_ == 'call' and _callstack_[-1] == 'main'
    - !until line 42
      !walk _line_ == 42 and _path_ == '/full/path/to/file.py'
    - !until path mymodule
      !walk 'mymodule' in _path_
    - !until exception ValueError
      !walk _exception_ is not None and 'ValueError' in type(_exception_).__name__
    - !until return success
      !walk _return_ is not None and 'success' in repr(_return_)
"""

HELP_GOTO = """    !goto <line>
    Jump execution to a specific line number in newest frame. Directly updates f_lineno.
    Invalid jumps fail; Python prevents jumps into/out of constructs like loops.
"""

HELP_CONTINUE = """    !continue
    Cleanly detach seapie and resume normal program execution without tracing overhead.
    To re-enter the debugger, another seapie.breakpoint() must be hit.
"""

HELP_VERBOSE = """    !verbose
    Toggle verbose output. When on, shows "stepping from" and "stopped at" messages
    during stepping, and mode change notifications. Default is on.
"""

HELP_PRETTY = """    !pretty
    Toggle prettyprinting of REPL output. When on, uses pprint to format output
    with proper indentation and line wrapping. Default is on.
"""
