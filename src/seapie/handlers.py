"""
bang handler stuff and related tools
all bang handlers folow the same format (frame, event, arg, bang_arg)
"""

import inspect
import sys

import seapie.helpers
import seapie.prompt


def do_help(_frame, _event, _arg, _bang_arg):
    print("nice")


def do_quit(_frame, _event, _arg, _bang_arg):
    exit()






def do_up(frame, _event, _arg, bang_arg):
    """Change the current working frame in repl loop. up ascend"""
    if frame.f_back is not None:
        seapie.helpers.show_callstack(frame.f_back)
        raise seapie.helpers.Frame(frame.f_back)
    print("Not enough frames in callstack to move up!")

def do_down(frame, _even, _arg, bang_arg):
    """down"""
    lower_f = next((i.frame for i in inspect.stack()[3:] if i.frame.f_back == frame), None)
    if lower_f is not None:
        seapie.helpers.show_callstack(lower_f)
        raise seapie.helpers.Frame(lower_f)
    print("Not enough frames in callstack to move down!")





def do_step(frame, _event, _arg, _bang_arg):
    if frame != inspect.stack()[3].frame:  # seapie occupies frames 0-2. 3 is top of stack.
        print("Note: step happened outside of selected frame.")
    raise seapie.helpers.Step  # step, dont update current working frame since trace fucnction is called again and gets a new frame

def do_continue(_frame, _event, _arg, _bang_arg):
    inspect.stack()[3].frame.f_trace = None  # seapie occupies frames [0-2], get actual top of stack. cant use _frame because it might be random working frame
    sys.settrace(None)  # todo: joka frameen None
    sys.displayhook = seapie.helpers.displayhook_factory(pretty=False)
    raise seapie.helpers.Step

def do_jump(frame, _event, _arg, bang_arg):
    """goto"""
    try:
        frame.f_lineno = int(bang_arg)
    except Exception as e:
        print("Jump failed:", str(e))
    else:
        print("Jump succeeded. Next line to execute is", bang_arg)







def do_where(_frame, _event, _arg, _bang_arg):
    seapie.helpers.show_traceback(frames_to_hide=4)

def do_list(frame, _event, _arg, _bang_arg):
    seapie.helpers.show_source(frame)

def do_prettyprint(_frame, _event, _arg, _bang_arg):
    """Toggles prettyprinting via displayhook"""
    displayhook_factory_pretty = sys.displayhook.__closure__[0].cell_contents
    if displayhook_factory_pretty:
        sys.displayhook = seapie.helpers.displayhook_factory(pretty=False)
        print("Prettyprinting is now off")
    else:
        sys.displayhook = seapie.helpers.displayhook_factory(pretty=True)
        print("Prettyprinting is now on")












def do_info(frame, _event, _arg, _bang_arg):
    seapie.helpers.show_callstack(frame)






















def do_to(_frame, _event, _arg, bang_arg):
    """to lineno"""
    raise NotImplementedError("to lineno")
    # try:
    #     num = int(bang_arg)
    #     assert num > 0
    # except Exception:
    #     pass
    # else:
    #     num = None

    # if num is None:
    #     pass

    # if bang_arg not in ("line", "call", "return", "exception"):
    #     print('The argment must be one of ("line", "call", "return", "exception")')
    # else:
    #     print("Setting event to", bang_arg)
    #     seapie.prompt.skip_handler.until = bang_arg
    #     raise seapie.helpers.Step



def do_event(frame, event, arg, _bang_arg):
    """until event"""
    raise NotImplementedError("to event")
    #seapie.helpers.show_info(frame, event, arg)