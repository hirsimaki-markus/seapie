"""!command handlers go here"""

import builtins
import inspect

import seapie.constants
import seapie.helpers
import seapie.repl

def get_command_help(name):
    """Return the HELP_* constant for a command name (supports aliases)"""
    # Map command names to their help constants
    help_map = {
        "help":      seapie.constants.HELP_HELP,
        "location":  seapie.constants.HELP_LOCATION,
        "traceback": seapie.constants.HELP_TRACEBACK,
        "step":      seapie.constants.HELP_STEP,
        "event":     seapie.constants.HELP_EVENT,
        "until":     seapie.constants.HELP_UNTIL,
        "walk":      seapie.constants.HELP_WALK,
        "frame":     seapie.constants.HELP_FRAME,
        "goto":      seapie.constants.HELP_GOTO,
        "continue":  seapie.constants.HELP_CONTINUE,
        "pretty":    seapie.constants.HELP_PRETTY,
        "verbose":   seapie.constants.HELP_VERBOSE,
        "keep":      seapie.constants.HELP_KEEP,
    }
    # Add first-letter aliases
    for full_name in list(help_map.keys()):
        help_map[full_name[0]] = help_map[full_name]
    return help_map.get(name)


def get_command(name):
    """Maps a !command string name to (handler, arg_counts, requires_top_frame).

    - handler: !command handler func(args) -> None, sets STATE["signal"]
    - arg_count: int for fixed arity, or "1+" for expression args (1 or more)
    - requires_top_frame: True if user must be at top of callstack to use this command
    Handlers access seapie.repl.STATE directly for working_frame, event, signal, and
    other global state. Single letter aliases are auto-generated (e.g. !h for !help).

    Command handler signature:
        do_*(args) -> None
        args:   List of arguments from user input (e.g. ["small"] for "!step small")
        Handlers access global state via seapie.repl.STATE (including event type)
        Signal meanings (set via STATE["signal"]):
            - "continue": Continue the repl loop in the current working frame
            - "walk":     Step code until the walk condition is met
            - "detach":   Detach the debugger and resume normal execution
    """
    #               handler      arg_count  top_frame
    commands = {
        "help":     (do_help,      0,        False),
        "location": (do_location,  0,        False),
        "traceback":(do_traceback, 0,        False),
        "step":     (do_step,      1,        True),
        "event":    (do_event,     1,        True),
        "until":    (do_until,     2,        True),
        "walk":     (do_walk,      "1+",     True),
        "frame":    (do_frame,     1,        False),
        "goto":     (do_goto,      1,        True),
        "continue": (do_continue,  0,        False),
        "pretty":   (do_pretty,    0,        False),
        "verbose":  (do_verbose,   0,        False),
        "keep":     (do_keep,      "1+",     False),
    }
    # Add first-letter aliases (must not collide)
    for full_name in list(commands.keys()):
        alias = full_name[0]
        if alias in commands:
            raise RuntimeError(f"Alias '{alias}' collides. This should never happen.")
        commands[alias] = commands[full_name]
    return commands.get(name)

def do_location(_args):
    """Show source code of the frame that is currently being inspected by the repl."""
    frame = seapie.repl.STATE["working_frame"]
    event = seapie.repl.STATE["event"]
    seapie.helpers.show_source(frame, event)
    seapie.repl.STATE["signal"] = "continue"


def do_traceback(_args):
    """Show callstack as traceback with current frame highlighted."""
    frame = seapie.repl.STATE["working_frame"]
    # 4 hides: [0]=show_tb, [1]=do_traceback, [2]=handle_user_input_command, [3]=loop
    seapie.helpers.show_tb(frames_to_hide=4, repl_tb=False, highlight_frame=frame)
    seapie.repl.STATE["signal"] = "continue"


def do_frame(args):
    """Navigate the callstack

    !frame up    -> move to caller frame (older)
    !frame down  -> move to callee frame (newer)
    !frame home  -> return to original frame (where debugger stopped)
    """
    frame = seapie.repl.STATE["working_frame"]
    direction = args[0]

    if direction == "up":
        f_back = frame.f_back
        up = seapie.constants.UP
        if f_back is None:
            print(f"{up}  Can't move higher (try !frame <down/home>)")
        else:
            print(f"{up}  frame up: {seapie.helpers.short_frame_info(f_back)}")
            seapie.repl.STATE["working_frame"] = f_back

    elif direction == "down":
        # Find the frame whose f_back is the current frame (i.e. the callee)
        # Magic number 3 skips seapie's internal frames in inspect.stack()
        stack = inspect.stack()[3:]
        callee = None
        for fi in stack:
            if fi.frame.f_back == frame:
                callee = fi.frame
                break
        down = seapie.constants.DOWN
        if callee is None:
            print(f"{down}  Can't move lower (try !frame <up/home>)")
        else:
            print(f"{down}  frame down: {seapie.helpers.short_frame_info(callee)}")
            seapie.repl.STATE["working_frame"] = callee

    elif direction == "home":
        original_frame = seapie.repl.STATE["original_frame"]
        if original_frame is None or frame is original_frame:
            print(f"{seapie.constants.HOME}  Already at home frame")
        else:
            short_info = seapie.helpers.short_frame_info(original_frame)
            print(f"{seapie.constants.HOME}  frame home: {short_info}")
            seapie.repl.STATE["working_frame"] = original_frame

    else:
        print(f"{seapie.constants.SKULL}  Do !frame to view help")

    seapie.repl.STATE["signal"] = "continue"


def do_walk(args):
    """Step forward until a Python expression evaluates to True

    This is the user-facing walk command. It sets tracing mode (to capture all events)
    and delegates to start_walk which sets STATE["signal"].

    example: !walk _line_ == 10 and _source_ == "print('Hello, world!')"
    """
    # Always use tracing mode for user !walk - they may need any event type
    seapie.helpers.set_trace_mode("tracing")
    seapie.helpers.start_walk(args[0])


def do_step(args):
    """Relative stepping - move forward by events or lines

    !step small        -> next debug event (smallest possible step)
    !step into / line  -> next line event anywhere (pdb's 'step')
    !step over / next  -> next line in current frame only (pdb's 'next')
    !step out / return -> step out of current function (pdb's 'return')
    """
    current_depth = len(builtins._callstack_)
    mode = args[0]

    # Normalize IDE terminology to internal names
    aliases = {"into": "line", "over": "next", "out": "return"}
    mode = aliases.get(mode, mode)

    # Map mode to walk condition
    conditions = {
        "small":  "True",
        "line":   "_event_ == 'line'",
        "next":   f"_event_ == 'line' and len(_callstack_) <= {current_depth}",
        "return": f"_event_ == 'return' and len(_callstack_) <= {current_depth}",
    }
    condition = conditions.get(mode)

    if condition is None:
        print(f"{seapie.constants.SKULL}  Unknown mode '{mode}'. Do !step to view help")
        seapie.repl.STATE["signal"] = "continue"
        return

    # Profiling mode is faster for return-only; tracing needed for line events
    seapie.helpers.set_trace_mode("profiling" if mode == "return" else "tracing")
    seapie.helpers.start_walk(condition)


def do_event(args):
    """Step until a specific event type occurs

    !event line       -> next line event
    !event call       -> next function call
    !event return     -> next function return
    !event exception  -> next exception
    """
    event_type = args[0]

    # Map event type to walk condition
    conditions = {
        "line":      "_event_ == 'line'",
        "call":      "_event_ == 'call'",
        "return":    "_event_ == 'return'",
        "exception": "_event_ == 'exception'",
    }
    condition = conditions.get(event_type)

    if condition is None:
        print(f"{seapie.constants.SKULL}  Do !event to view help")
        seapie.repl.STATE["signal"] = "continue"
        return

    # Profiling mode is faster for call/return; tracing needed for line/exception
    mode_needed = "profiling" if event_type in ("call", "return") else "tracing"
    seapie.helpers.set_trace_mode(mode_needed)
    seapie.helpers.start_walk(condition)


def do_until(args):
    """Step until a targeted condition is met

    !until enter <func>      -> stop when entering function <func>
    !until line <number>     -> stop at line <number> in current file
    !until source <text>     -> stop when source line contains <text>
    !until path <text>       -> stop when filepath contains <text>
    !until exception <text>  -> stop when exception type name contains <text>
    !until return <text>     -> stop when return value contains <text>
    """
    frame = seapie.repl.STATE["working_frame"]
    kind, target = args[0], args[1]
    filepath = frame.f_code.co_filename

    # Build condition based on kind
    if kind == "enter":
        expression = f"_event_ == 'call' and _callstack_[-1] == {repr(target)}"
    elif kind == "line":
        try:
            lineno = int(target)
        except ValueError:
            print(f"{seapie.constants.SKULL}  Invalid line number: {target}")
            seapie.repl.STATE["signal"] = "continue"
            return
        expression = f"_line_ == {lineno} and _path_ == {repr(filepath)}"
    elif kind == "source":
        expression = f"{repr(target)} in _source_"
    elif kind == "path":
        expression = f"{repr(target)} in _path_"
    elif kind == "exception":
        expression = (
            f"_exception_ is not None and {repr(target)} in type(_exception_).__name__"
        )
    elif kind == "return":
        expression = f"_return_ is not None and {repr(target)} in repr(_return_)"
    else:
        print(f"{seapie.constants.SKULL}  Do !until to view help")
        seapie.repl.STATE["signal"] = "continue"
        return

    # Profiling mode is faster for enter/return; tracing needed for others
    mode_needed = "profiling" if kind in ("enter", "return") else "tracing"
    seapie.helpers.set_trace_mode(mode_needed)
    seapie.helpers.start_walk(expression)


def do_continue(_args):
    """Detach the debugger and resume normal program execution."""
    print(f"{seapie.constants.DETACH}  Detaching seapie (original program continues)")
    seapie.helpers.clear_trace()
    seapie.repl.STATE["signal"] = "detach"


def do_pretty(_args):
    """Toggle prettyprinting of REPL output."""
    seapie.repl.STATE["pretty"] = not seapie.repl.STATE["pretty"]
    if seapie.repl.STATE["pretty"]:
        print(f"{seapie.constants.PRETTYON}  Prettyprinting on")
    else:
        print(f"{seapie.constants.PRETTYOFF}  Prettyprinting off")
    seapie.repl.STATE["signal"] = "continue"


def do_verbose(_args):
    """Toggle verbose output (stepping messages, mode change messages)."""
    seapie.repl.STATE["verbose"] = not seapie.repl.STATE["verbose"]
    if seapie.repl.STATE["verbose"]:
        print(f"{seapie.constants.STEP}  Verbose mode on")
    else:
        print(f"{seapie.constants.STEP}  Verbose mode off")
    seapie.repl.STATE["signal"] = "continue"


def do_goto(args):
    """Jump execution to a specific line number in the current frame."""
    frame = seapie.repl.STATE["working_frame"]
    lno = args[0]
    try:
        frame.f_lineno = int(lno)
        print(f"{seapie.constants.JUMP}  Jump succeeded. Next line to execute is {lno}")
    except Exception as e:
        print(f"{seapie.constants.SKULL}  Jump failed {e}. Do !goto to view help")
    seapie.repl.STATE["signal"] = "continue"


def do_keep(args):
    """keep an expression - display its value at the top of the terminal

    !keep None    -> clear the keep'd expression
    !keep <expr>  -> set expression to keep
    """
    seapie.helpers.clear_keep_display()
    expr = args[0]

    if expr == "None":
        seapie.repl.STATE["keep_expression"] = None
        print(f"{seapie.constants.EYE}  Cleared keep'd expression")
    else:
        try:
            compile(expr, "<string>", "eval")
        except SyntaxError as e:
            print(f"{seapie.constants.SKULL}  Invalid expression {repr(expr)}: {e}")
            seapie.repl.STATE["signal"] = "continue"
            return
        seapie.repl.STATE["keep_expression"] = expr
        print(f"{seapie.constants.EYE}  keeping: {expr}")

    seapie.helpers.show_keep_value()
    seapie.repl.STATE["signal"] = "continue"


def do_help(_args):
    """Show the internal help message."""
    seapie.helpers.show_help()
    seapie.repl.STATE["signal"] = "continue"
