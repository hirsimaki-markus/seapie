"""Helpers used by seapie.repl and seapie.commands. Not intended for direct use."""

import builtins
import contextlib
import inspect
import pathlib
import platform
import pprint
import shutil
import signal
import sys
import pydoc
import threading
import traceback
import textwrap

import seapie.constants
import seapie.repl

# Used to ensure VT100 prints that move cursor can't be garbled by other threads
KEEP_DISPLAY_LOCK = threading.Lock()


def invert(text):
    """Wrap text with VT100 invert codes for highlighted display."""
    return f"{seapie.constants.VT_INV}{text}{seapie.constants.VT_RESET}"


def sigint_handler(_signum, _frame):
    """SIGINT handler during walks - sets flag instead of raising KeyboardInterrupt.

    This prevents Ctrl+C from propagating into the traced code and corrupting its state.
    The walk will stop at the next trace event when check_walk_condition sees the flag.
    """
    # Ctrl+c pressed, stop at next event
    seapie.repl.STATE["walk_interrupted"] = True


def install_sigint_handler():
    """Install walk-safe SIGINT handler, save original for later restore."""
    seapie.repl.STATE["walk_interrupted"] = False
    seapie.repl.STATE["original_sigint"] = signal.signal(signal.SIGINT, sigint_handler)


def restore_sigint_handler():
    """Restore original SIGINT handler after walk ends."""
    if seapie.repl.STATE["original_sigint"] is not None:
        signal.signal(signal.SIGINT, seapie.repl.STATE["original_sigint"])
        seapie.repl.STATE["original_sigint"] = None
    seapie.repl.STATE["walk_interrupted"] = False


def start_walk(condition):
    """Start a walk with the given condition. Caller must set mode first.

    Shows first-step tip (once per session), stepping-from message, validates condition.
    Sets STATE["signal"] to "walk" or "continue" on error.
    SIGINT handler is installed to stop walk on Ctrl+C.
    """
    if not seapie.repl.STATE["first_walk_done"]:
        seapie.repl.STATE["first_walk_done"] = True
        print(textwrap.dedent("""
            ┌─────────────────── once-per-session tip ───────────────────┐
            │ Use !verbose to hide per-step messages and check out !keep │
            │ Use Ctrl+C to interrupt long-running stepping              │
            └────────────────────────────────────────────────────────────┘"""[1:])
        )

    try:
        compile(condition, "<string>", "single")
    except (SyntaxError, ValueError, TypeError) as e:
        issue = f"{repr(condition)}: {str(e)}"
        print(f"{seapie.constants.SKULL}  Bad condition {issue}. Do !walk to view help")
        seapie.repl.STATE["signal"] = "continue"
        return

    if seapie.repl.STATE["verbose"]:
        frame = seapie.repl.STATE["working_frame"]
        print(f"{seapie.constants.STEP}  stepping from: {short_frame_info(frame)}")
    seapie.repl.STATE["walk_condition"] = condition
    install_sigint_handler()
    seapie.repl.STATE["signal"] = "walk"


def short_frame_info(frame):
    """Return concise frame info string: 'func()  (filename:lineno)'"""
    func = frame.f_code.co_name
    filename = pathlib.Path(frame.f_code.co_filename).name
    lineno = frame.f_lineno
    return f"{func}()  ({filename}:{lineno})"


def set_trace_mode(mode):
    """Set debugging mode: tracing (all events) or profiling (fast, call/return only).

    Used internally by stepping commands for optimization. Not user-facing.
    """
    verbose = seapie.repl.STATE["verbose"]

    if mode == "tracing" and sys.gettrace() is None:
        sys.setprofile(None)
        sys.settrace(seapie.repl.loop)
        if verbose:
            print(f"{seapie.constants.SLOW}  tracing call/return/line/exception events")

    if mode == "profiling" and sys.getprofile() is None:
        sys.settrace(None)
        sys.setprofile(seapie.repl.loop)
        if verbose:
            print(f"{seapie.constants.FAST}  tracing call/return events")


def show_help():
    """Assemble and display help from HELP_* constants. Enter to scroll."""
    text = "\n".join([
        seapie.constants.HELP_HEADER,
        seapie.constants.HELP_BRIEF,
        seapie.constants.HELP_QUICKSTART,
        seapie.constants.HELP_QUICKLIST,
        seapie.constants.HELP_MAGIC,
        seapie.constants.HELP_COMMAND_REFERENCE_HEAD,
        seapie.constants.HELP_HELP,
        seapie.constants.HELP_LOCATION,
        seapie.constants.HELP_TRACEBACK,
        seapie.constants.HELP_FRAME,
        seapie.constants.HELP_KEEP,
        seapie.constants.HELP_STEP,
        seapie.constants.HELP_EVENT,
        seapie.constants.HELP_UNTIL,
        seapie.constants.HELP_WALK,
        seapie.constants.HELP_GOTO,
        seapie.constants.HELP_CONTINUE,
        seapie.constants.HELP_VERBOSE,
        seapie.constants.HELP_PRETTY,
    ])
    pydoc.pager(text)


def get_term_width():
    return shutil.get_terminal_size()[0]


def displayhook(obj):
    """Used with sys.displayhook. Implements prettyprinting and mimics the _ in repl.

    Set by breakpoint() and cleared by clear_trace().
    """
    if obj is not None:
        if seapie.repl.STATE["pretty"]:
            pprint.pp(obj, width=get_term_width())
        else:
            print(obj)
        builtins._ = obj  # Store the new value as _.


def is_traceable(frame, event):
    """Return True if this frame/event should be traced by seapie, False to skip.

    Filters out:
    - Unhandled events: setprofile emits c_call/c_return/c_exception for C functions
      (like len(), print()); settrace emits opcode if frame.f_trace_opcodes=True.
      We only handle: call, line, return, exception.
    - Unhandled exception processing: When sys.last_exc is set, Python is processing
      an unhandled exception and we should not interfere (would trace internals).
    - Internal seapie code objects
    - exit(): Don't trace the python internal exit process
    - breakpoint(): Don't trace our own entry point
      - displayhook(): Python's REPL calls sys.displayhook after every expression.
        Since seapie sets sys.displayhook = displayhook, this would cause the
        debugger to trace its own output machinery instead of user code. This issue only
        happens if seapie is outside of a script.
    """
    # Filter events we don't handle
    if event not in ("call", "line", "return", "exception"):
        return False

    # Don't trace during unhandled exception processing
    if hasattr(sys, "last_exc"):
        return False

    # Don't trace seapie's own code
    excluded_codes = (
        exit.__call__.__code__,
        seapie.breakpoint.__code__,
        displayhook.__code__,
    )
    if frame.f_code in excluded_codes:
        return False

    return True


def show_source(frame, event, context=50):
    """Show source code around the current line with the current line highlighted.

    Displays up to 'context' lines before and after the current line.
    Current line is shown with inverted colors.
    """
    term_width = get_term_width()
    filepath = frame.f_code.co_filename

    # Header
    print(f" file: {filepath} ".center(term_width, "-"))
    try:
        lines = pathlib.Path(filepath).read_text().splitlines()
    except Exception:
        print(f"  Can't read source: {pathlib.Path(filepath).name}")
        return

    # Print source code
    start = max(frame.f_lineno - context, 1)  # Ensure start is at least 1.
    end = min(frame.f_lineno + context, len(lines))  # Ensure end doesn't hit EOF.
    for lineno in range(start, end + 1):
        lno_str = str(lineno).rjust(len(str(end)) + 2)  # Align line numbers.
        line_content = f"{lno_str} {lines[lineno - 1].rstrip()}"[:term_width]
        if lineno == frame.f_lineno:
            print(invert(line_content))
        else:
            print(line_content)

    # Footer + one extra reset at end to ensure it happens after all prints in case of
    # cropped output
    print(f"{seapie.constants.VT_RESET} debug event: {event} ".center(term_width, "-"))


def update_magic_variables(f, event, arg):
    """Based on current working frame, update magic vars in builtins for use in repl.
    builtins allows shadowing locals and globals without overwriting them
    """
    cl = ""  # Source line.
    with contextlib.suppress(Exception):
        cl = pathlib.Path(f.f_code.co_filename).read_text().splitlines()[f.f_lineno - 1]
    builtins._line_ = f.f_lineno
    builtins._source_ = cl
    builtins._path_ = f.f_code.co_filename
    builtins._return_ = arg if event == "return" else None
    builtins._exception_ = arg[1] if event == "exception" else None  # Full exc object
    builtins._event_ = event
    # Skip seapie frames: [0]=update_magic_variables, [1]=check_walk_condition, [2]=loop
    builtins._callstack_ = list(reversed([i.function for i in inspect.stack()[3:]]))
    # Dict of all magic variables for convenience
    builtins._magic_ = {
        "_line_": builtins._line_,
        "_source_": builtins._source_,
        "_path_": builtins._path_,
        "_return_": builtins._return_,
        "_exception_": builtins._exception_,
        "_event_": builtins._event_,
        "_callstack_": builtins._callstack_,
    }


def check_walk_condition():
    """Check walk condition and return whether to keep walking.

    Evaluates walk condition if set. Checks the walk_interrupted flag
    (set by SIGINT handler) for graceful Ctrl+C.

    Returns:
        "keep_walking" - condition not met, continue stepping
        "stop" - condition met, error occurred, or Ctrl+C pressed; enter REPL

    Side effects:
        - Clears walk_condition in STATE when stopping
        - Restores tracing mode and SIGINT handler when stopping
    """
    if seapie.repl.STATE["walk_condition"] is None:
        return "stop"  # No walk active, enter REPL

    frame = seapie.repl.STATE["original_frame"]

    # Check if Ctrl+C was pressed (flag set by sigint_handler)
    if seapie.repl.STATE["walk_interrupted"]:
        print(f"{seapie.constants.STOP}  Walk interrupted")
        seapie.repl.STATE["walk_condition"] = None
        restore_sigint_handler()
        set_trace_mode("tracing")
        return "stop"

    try:
        condition_met = eval(
            seapie.repl.STATE["walk_condition"],
            frame.f_globals,
            frame.f_locals
        )
    except Exception as e:
        problem = f"Walk condition error, stopping: {type(e).__name__}: {e}"
        print(f"{seapie.constants.SKULL}  {problem}. Do !walk to view help")
        condition_met = True  # Stop on error

    if not condition_met:
        return "keep_walking"

    # Condition met, clear walk and restore handlers
    if seapie.repl.STATE["verbose"]:
        print(f"{seapie.constants.STEP}  stopped at: {short_frame_info(frame)}")
    seapie.repl.STATE["walk_condition"] = None
    restore_sigint_handler()
    set_trace_mode("tracing")
    return "stop"


def clear_trace():
    """Stop all tracing and profiling, clear _ from displayhook, clear magic vars."""
    sys.settrace(None)
    for f in inspect.stack():
        f.frame.f_trace = None
    # Clear magic variables: "_" (last result), all in _magic_, and _magic_ itself
    names_to_clear = ["_", "_magic_"] + list(getattr(builtins, "_magic_", {}).keys())
    for name in names_to_clear:
        if hasattr(builtins, name):
            delattr(builtins, name)
    sys.setprofile(None)
    sys.displayhook = sys.__displayhook__


def breakpoint(show_banner=True):
    """Roughly equivalent to pdb.set_trace. Call this to start a repl (>>> ... ...)."""
    if sys.gettrace() is seapie.repl.loop or sys.getprofile() is seapie.repl.loop:
        return  # Don't trace own breakpoint or repl loop.
    if sys.gettrace() is not None or sys.getprofile() is not None:
        raise RuntimeError("Can't trace. Another tracer or profiler already in use.")

    sys.displayhook = displayhook  # Displayhook for prettyprinting and _ in repl.
    with contextlib.suppress(ImportError):
        import readline  # Needed for line editing if available.
    if hasattr(sys, "ps1"):  # Detect if in interactive interpreter
        print(
            "! -------------------------------------------------------------------- !\n"
            "!           seapie behaviour outside of scripts is undefined           !\n"
            "!     If debugging a script: 'import seapie; seapie.breakpoint()'      !\n"
            "! If testing out seapie: python -c 'import seapie;seapie.breakpoint()' !\n"
            "! -------------------------------------------------------------------- !"
        )
    print(f"{seapie.constants.ATTACH}  Attaching seapie")
    if show_banner:
        ver = sys.version.split()[0]  # Extract Python version
        compiler = platform.python_compiler()  # Get compiler info
        os_name = sys.platform  # Get OS name

        print(f"seapie {seapie.__version__} (Python {ver}) [{compiler}] on {os_name}")
        print('Type "!help" for seapie help')

    sys.settrace(seapie.repl.loop)  # Start the actual tracing. This must be done last.
    frame = sys._getframe(1)  #  Trace is set last as after it this func loses control.
    while frame:  # The control is returned to this function after tracing is stopped.
        frame.f_trace = seapie.repl.loop
        frame = frame.f_back  # Loop will update magic variables. No need to do it here.


def clear_keep_display():
    """Clear the keep display area at top of terminal (max 7 lines)."""
    with KEEP_DISPLAY_LOCK:
        max_box_lines = 7  # header + 5 content + footer
        output = seapie.constants.VT_SAVE
        for i in range(max_box_lines):
            output += f"\033[{i+1};1H{seapie.constants.VT_CLEARLINE}"
        output += seapie.constants.VT_RESTORE
        print(output, end="", flush=True)


def show_keep_value():
    """Evaluate and display the kept expression in a box at the top of the terminal.

    Uses a lock to prevent garbled output if another thread writes concurrently.
    """
    def _box_line(left_corner, right_corner, label, width):
        """Build a box line like: ┌─── label ───┐ or └─── label ───┘"""
        H = seapie.constants.BOX_H
        label_display = f" {label} " if label else ""
        dashes_needed = width - len(label_display)
        left = dashes_needed // 2
        right = dashes_needed - left
        return f"{left_corner}{H * left}{label_display}{H * right}{right_corner}"

    keep_expression = seapie.repl.STATE["keep_expression"]
    if keep_expression is None:
        return

    frame = seapie.repl.STATE["working_frame"]

    term_width, term_height = shutil.get_terminal_size()
    min_width = 40   # Minimum sensible terminal width for the box
    min_height = 10  # Need room for box (up to 7 lines) plus REPL

    if term_width < min_width or term_height < min_height:
        # Terminal too small, show error at top and return
        error_msg = "<terminal too small for !keep>"[:term_width]
        c = seapie.constants
        with KEEP_DISPLAY_LOCK:
            print(
                f"{c.VT_SAVE}{c.VT_MOVETOP}{c.VT_CLEARLINE}"
                f"{error_msg}{c.VT_RESTORE}", end="", flush=True
            )
        return

    try:
        value = eval(keep_expression, frame.f_globals, frame.f_locals)
        value_str = repr(value)
    except Exception as e:
        value_str = f"<{type(e).__name__}: {e}>"

    box_width = term_width - 2  # Account for │ on each side
    V = seapie.constants.BOX_V
    TL, TR = seapie.constants.BOX_TL, seapie.constants.BOX_TR
    BL, BR = seapie.constants.BOX_BL, seapie.constants.BOX_BR

    # Build header line: ┌──── expr ────┐
    # Truncate expression if too long (leave room for corners + min 2 dashes each side)
    max_expr_len = box_width - 4
    if len(keep_expression) > max_expr_len:
        expr_label = f"{keep_expression[:max_expr_len - 3]}..."
    else:
        expr_label = keep_expression
    header = _box_line(TL, TR, expr_label, box_width)

    # Wrap value to fill up to max_lines, discard the rest
    max_lines = 5
    content_width = box_width - 2  # Space for padding inside │ │

    # Replace actual newlines with visible symbol to prevent box corruption
    value_str = value_str.replace('\n', '↵')

    # Wrap by chunking the entire value string
    wrapped_lines = []
    remaining = value_str
    while remaining and len(wrapped_lines) < max_lines:
        wrapped_lines.append(remaining[:content_width])
        remaining = remaining[content_width:]

    # Build content lines with box borders
    content_lines = []
    for line in wrapped_lines:
        padded = f"{V} {line.ljust(content_width)} {V}"
        content_lines.append(padded)

    # Footer line - show truncation info if applicable
    truncated_chars = len(remaining)
    if truncated_chars > 0:
        footer = _box_line(BL, BR, f"truncated {truncated_chars} chars", box_width)
    else:
        footer = _box_line(BL, BR, "", box_width)

    # Build full box and output with VT100 cursor control
    box_lines = [header] + content_lines + [footer]
    output = (
        seapie.constants.VT_SAVE + seapie.constants.VT_MOVETOP + "\n".join(box_lines) +
        seapie.constants.VT_RESTORE
    )
    with KEEP_DISPLAY_LOCK:
        print(output, end="", flush=True)


def show_tb(frames_to_hide, repl_tb, highlight_frame=None):
    """Show traceback without seapie frames.
    frames_to_hide: # of seapie frames
    repl_tb: show exc from repl.
    highlight_frame: optional frame object to invert colors for in the output.
    """
    ex_type, ex, ex_tb = sys.exc_info()  # Capture exception info if any
    if highlight_frame is not None:
        print(
            f"Traceback (most recent call last, working frame highlighted):",
            file=sys.stderr
        )
    else:
        print("Traceback (most recent call last):", file=sys.stderr)

    # Get stack without seapie frames and format with optional highlighting
    stack = traceback.extract_stack(sys._getframe(frames_to_hide))
    for fs in stack:
        formatted = traceback.format_list([fs])[0]
        # Check if this frame should be highlighted with inverted colors
        if highlight_frame is not None:
            if (fs.filename == highlight_frame.f_code.co_filename and
                fs.lineno == highlight_frame.f_lineno and
                fs.name == highlight_frame.f_code.co_name):
                # Wrap each line with invert codes
                lines = formatted.rstrip('\n').split('\n')
                lines = [invert(line) for line in lines]
                formatted = '\n'.join(lines) + '\n'
        print(formatted, end="")

    if repl_tb:  # If True, show frames of exception generated in seapie repl.
        # [2:] hides: [0]=handle_user_input_exec, [1]=exec call
        print("".join(traceback.format_list(traceback.extract_tb(ex_tb)[2:])), end="")
    if ex_type is not None:  # Show "TypeError: wrong type" or such if exception exists.
        print(f"{ex_type.__name__}{': ' + str(ex) if str(ex) else ''}", file=sys.stderr)
