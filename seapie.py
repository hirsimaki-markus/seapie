"""Seapie debugger. Usage: import seapie;seapie.seapie() and enter !help

For advanced use seapie accepts autoexecutable string that will be
consumed before user is queried in the repl. Breakpoints can further
extend the autoexecutable list. Note that breakpoints DO clear existing
!until commands
    Example:
        import seapie;seapie.seapie(["print('first!')"], "!verbose")

SEAPIE stands for Scope Escaping Arbitary Python Injection Executor
To begin tracing call seapie.seapie() and to set breakpoint add more
seapie.seapie() calls to breakpoint the active tracing.

Distrubuted under the unlisence in 2019 and 2020 by Markus Hirsimäki

    ><> ><> ><>             ><> ><>
        <>< <>< <>< <><         <>< <>< <>< <><
            ><> ><> ><> ><>     ><>#####><> ><> ><>
            <><#####<>< <>< <>< <>< <><#####<>< <>< <><
            ><> ><>#####><> ><> ><>#####><>#####><> ><> ><>
                <>< <><#####<><#####<>< <>< <><#####<>< <><
                    ><> ><>#####><> ><>     ><> ><>#####><> ><>
                        <>< ### <><             <>< <><#<>< <>< <><
                    ><> ><>#####><> ><>     ><> ><>#####><> ><>
                <>< <><#####<><#####<>< <>< <><#####<>< <><
            ><> ><>#####><> ><> ><>#####><>#####><> ><> ><>
            <><#####<>< <>< <>< <>< <><#####<>< <>< <><
            ><> ><> ><> ><>     ><>#####><> ><> ><>
        <>< <>< <>< <><         <>< <>< <>< <><
    ><> ><> ><>             ><> ><>

"""


import sys
import inspect
import traceback
from code import compile_command
from ctypes import pythonapi, py_object, c_int
from codeop import compile_command as compile_cmd_codeop


class SingletonException(Exception):
    """Raised when Seapie object is trying to be initialized"""
    pass


class SeapieReplExitException(Exception):
    """raised to close seapie repl"""
    pass


class Seapie:
    """Use 'import seapie;seapie.seapie()' and enter !help
    
    This class is instanceless container. Do not make seapie objects.
    All information is stored in class attributes and the class should
    be treted as singleton
    """
    exit_permanently = False  # implements !quit to ignore breakpoints
    until_expr = None  # implements '!until expression' magic command
    until_line = None  # implements '!until linenumber' magic command
    verbose = True  # if "executed line ..." messages should be printed
    command_list = []
    scope = 0

    def __init__(self):
        """Init should not be used. Seapie is logical singleton class"""
        raise SingletonException("The Seapie class is a logical and ",
        "instanceless singleton! Access it with import seapie;seapie()")

    @classmethod
    def seapie(cls, command_list=None):
        """This function starts tracing or breakpoints active tracing
 
        This function wraps setting call and line tracing
        """
        if not cls.exit_permanently:  # this flag implements !quit
        
            if command_list is not None:
                cls.command_list.extend(command_list)
        
            if sys.gettrace() is not None:
                # seapie() already tracing. treat new call as breakpoint
                print("Stopping on breakpoint")
                cls.until_expr = None  # remove !until condition
                cls.until_line = None  # to enable interactive input
            else:
                # seapie() is not tracing yet. start tracing
                print("=" * 17 +
                      "[ Starting seapie 2.0 (enter !help for help) ]" +
                      "=" * 17)
                sys.settrace(cls._trace_calls)
                # setting trace function above will not start tracing
                # in current strack frame. get previous frame aka. the
                # parent that called seapie to begin tracing immediately
                sys._getframe(1).f_trace = cls._repl_and_tracelines

    @staticmethod
    def true_exec(code, scope):
        """exec() a codeblock in given scope. Used by seapi repl
        
        scope 0 equals executing in context of caller of true_exec().
        scope 1 equals executing in context of the caller for the caller
        of true_exec().
        """
        parent = sys._getframe(scope+1)  # +1 escapes true_exec itself
        parent_globals = parent.f_globals
        parent_locals = parent.f_locals
        try:
            exec(code, parent_globals, parent_locals)
        except KeyboardInterrupt:  # emulate ctrl+c if code='input()'
            print("\nKeyboardInterrupt")
        except Exception:  # catch arbitary exceptions from exec
            traceback.print_exc()
        # beware traveller. here lies dark spell of the olden times !
        # the following call forces update to locals()
        # adding new variables is allowed but calling them requires
        # some indirection like using exec() or a placeholder
        # otherwise you will get nameError when calling the variable
        # the magic value 1 stands for ability to introduce new
        # variables. 0 for update-only
        pythonapi.PyFrame_LocalsToFast(py_object(parent), c_int(1))

    @classmethod
    def _trace_calls(cls, frame, event, arg):
        """This is called when new stack frame is entered during tracing
        
        This funtion returns the actual interactive repl that is used to
        trace lines inside the entered stack frames
        """
        if frame.f_code.co_name == "seapie" :
            # seapie itself is not traced. it is treated as breakpoint
            return
        if cls.verbose:
            print("Executed line", frame.f_lineno, "entered",
                   frame.f_code.co_name, "in",
                   inspect.getsourcefile(frame))
        return cls._repl_and_tracelines  # return line tracing function

    @classmethod
    def _repl_and_tracelines(cls, frame, event, arg):
        """Line tracing, main injector repl and postmortem trigger"""
        try:  # postmortem check
            if str(type(arg[2])) == "<class 'traceback'>":
                # this test must be performed here as this function is
                # the line tracer. when this if block is true it means
                # unhandled exception happened and it should be treated
                # as breakpoint to allow for postmortem debugging
                cls.until_expr = None  # remove existing stepping rules
                cls.until_line = None  # remove existing stepping rules
                print()
                # print traceback before the crash actually happens
                traceback.print_exception(*arg)
                print()
                print("="*4 + "[ Starting postmortem to preserve state."
                      " Stepping throws the exception ]" + "="*4)
        except TypeError: # arg was none. no error. no postmortem
            pass
    
        while True:  # this is the main repl loop
            if cls.command_list:  # there are buffered commands incoming
                codeblock = cls.command_list.pop(0)  # consume command
            elif cls.until_line is None and cls.until_expr is None:
                # there are no buffered commands and no until statements
                codeblock = cls.get_codeblock()
            else:
                # _step_until_handler will return either a !step magic
                # string or get_codeblock()'s result if stepping is done
                codeblock = cls._step_until_handler(frame)
            # got codeblock. handle it
            if isinstance(codeblock, str):  # uncompiled code/magic
                if codeblock.startswith("!"):  # magic
                    try:
                        cls._magic_handler(codeblock)
                        continue  # magic handling is over, return to loop
                    except SeapieReplExitException:
                        # this is raised in magic handler if the repl
                        # should exit. magic handler never returns anything
                        return
                else:  # did not get magic string but an executable str
                    cls.true_exec(codeblock, cls.scope+1)  # +1 esc repl
            else:  # did not get magic string but an compiled object
                cls.true_exec(codeblock, cls.scope+1)  # +1 escapes repl

    @classmethod
    def _step_until_handler(cls, frame):
        """Wrapper function for get_codeblock that handles !until magic
        
        Returns plain text magic string !step or compiled code object
        (either valid expression or statement). !step magic string is
        automatically returned if required by !until condition given
        before in previous command.
        """
        if cls.until_line is not None:  # walk to line number
            if cls.until_line != frame.f_lineno:  # line is not reached
                return "!step"
            else:  # stepping has reached the target line
                cls.until_line = None  # reset condition
                return cls.get_codeblock()  # and return normal prompt
        elif cls.until_expr is not None:  # walk until expr is true
            try:  # nameError will happen in most scopes
                # eval is done in the executing scope. user CAN cause
                # side effects with strange !until expressions
                globals, locals = frame.f_globals, frame.f_locals
                if eval(cls.until_expr, globals, locals):  # force scope
                    # found variables, condition is True
                    cls.until_expr = None  # clear condition
                    return cls.get_codeblock()  # return to interactive
                else:  # found variables but condition is not True
                    return "!step"
            except NameError:
                # could not find variable to even try to satisfy
                # condition. skipping this line
                return "!step"

    @staticmethod
    def get_codeblock():
        """Fake python repl until function can return meaningful code.
        
        returns single compiled expression/statement or magic string"""
        accumulator = ""  # accumulator for multiline commands
        raw_text = ""  # single line input
        while True:  # stay open until something can be returned
            try:
                if not accumulator:  # on first line of incoming block
                    raw_text = input(str("(S2) " + sys.ps1))
                else:  # if on continuing line
                    raw_text = input(str("(S2) " + sys.ps2))
            except KeyboardInterrupt:  # emulate behaviour of ctrl+c
                print("\nKeyboardInterrupt")
                accumulator = ""
                continue
            except EOFError:  # emulate behaviour of ctrl+z
                sys.exit(1)
            if accumulator == "" and raw_text.startswith("!"):
                # got single line magic string like "!help"
                return raw_text
            # this block should catch situation where two newlines are
            # entered during function definition or other such things
            if raw_text == "":  # input was empty
                try:
                    # add the newline missing from previous input line
                    # this must be done here to avoid extra newlines
                    accumulator = "\n" + accumulator
                    # try to compile and except for comile errors
                    compile_cmd_codeop(accumulator, "<input>", "single")
                except:  # catch exceptions compiling and reset
                    traceback.print_exc()
                    accumulator = ""  # reset getting input. restart
                    continue
            # manually add newline after inputs. must be added after
            # input, not not the end of input
            accumulator += "\n" + raw_text
            try:
                result = compile_command(accumulator)
            except SyntaxError:  # not a valid command
                traceback.print_exc()
                accumulator = ""
                continue
            if result is None:  # incomplete but possibly valid command
                pass  
            else:
                return result  # valid command inputted

    @classmethod
    def _magic_handler(cls, magicstring):
        """This function handles magic strings inputted into repl"""
        if magicstring in ("!help", "!h"):
            help = ["",
            "===================[ seapie 2.0 help ]===================",
            "",
            "Features are listed here with their short explanations.",
            "Any line entered starting with ! is excepted by seapie",
            "and treated as magic command like !help. Anything else is",
            "intepreted like the python interpreted does.",
            "",
            "Breakpoint means any call to seapie.seapie() and tracing",
            "is started using the same call. Postmortem happens when",
            "seapie traces into unhandled error and is automatic.",
            "",
            "For advanced use seapie accepts autoexecutable strings",
            "that will be consumed before user is queried in the repl.",
            "Breakpoint can extend this list but it clears old !until",
            "Example:",
            "  import seapie;seapie.seapie(['print(123)'], '!verbose')",
            "",
            "(!h)elp       : Show this info block",
            "(!e)xit       : Close seapie, end tracing and resume main",
            "(!q)uit       : Exit and ignore future breakpoints",
            "(!v)erbose    : Toggles printing messages about exeution",
            "",
            "(!t)raceback  : Show traceback excluding seapie",
            "(!l)ocals     : locals() in prettyprinted from",
            "(!g)lobals    : globals() in prettyprinted from",
            "(!w)here      : Show executing line and it's surroundings",
            "                └─> utf-8 encoding assumed in source file",
            "",
            "(!n)amespace  : Show current scope/namespace name",
            "(!+)namespace : Go down in callstack towards global scope",
            "(!-)namespace : Go up in callstack towards local scope",
            "(!0)namespace : Go back to currently executing scope",
            "",
            "(!s)tep       : Execute the next line of source code",
            "(!r)un        : Step until next breakpoint or postmortem",
            "(!u)ntil 1234 : Step until source code line 1234 or until",
            "                next beakpoint or postmortem",
            "                └─> note: line must be executable code;",
            "                          not comment, def or class etc.",
            "(!u)ntil expr : Step until eval('my_expression') == True",
            "                or until next breakpoint or postmortem",
            "                ├─> e.g.: '!u x==10' or '!u bool(my_var)'",
            "                └─> note: eval is done in executing scope",
            "                          and you CAN cause side effects",
            "(!c)ode obj   : Show source code of eval('obj')",
            "                ├─> e.g.: code my_function_name",
            "                └─> note: you CAN eval with side effects",
            "",
            "=========================================================",
            ""]
            for line in help: print("    " + line)
        elif magicstring in ("!exit", "!e"):
            print("Continuing from line",
                   sys._getframe(cls.scope+2).f_lineno)
            sys.settrace(None)
            # disable tracing immediately. settrace works on next frames
            sys._getframe(cls.scope+2).f_trace = None
            raise SeapieReplExitException
        elif magicstring in ("!quit", "!q"):
            print("Continuing from line",
                   sys._getframe(cls.scope+2).f_lineno,
                   "and ignoring future breakpoints")
            sys.settrace(None)
            # disable tracing immediately. settrace works on next frames
            sys._getframe(cls.scope+2).f_trace = None
            # set flag to ignore future breakpoints
            cls.exit_permanently = True
            raise SeapieReplExitException
        elif magicstring in ("!verbose", "!v"):
            cls.verbose = not cls.verbose
            if cls.verbose:
                print("Verbose mode on")
            else:
                print("Verbose mode off")
        elif magicstring in ("!step", "!s"):
            if cls.scope != 0:
                print("Stepping disabled is disabled by seapie in "
                      "frames that are not executing. Use !0namespace "
                      "and then try again")
            else:
                if cls.verbose:
                    print("Executed line",
                           sys._getframe(cls.scope+2).f_lineno)
                    # stepping is caused by re-entering seapie
                    # SeapieReplExitException is used to exit seapie
                    # and it is re-entered because of tracing
                raise SeapieReplExitException
        elif magicstring in ("!run", "!r"):
            if cls.scope != 0:
                print("Stepping disabled is disabled by seapie in "
                      "frames that are not executing. Use !0namespace "
                      "and then try again")
                return
            # run until breakpoint or postmortem. always evals to False
            cls.until_expr = "False"
        elif (magicstring[:7] in ("!until ", "!until")
             or magicstring[:3] in ("!u ", "!u")):
            if cls.scope != 0:
                print("Stepping disabled is disabled by seapie in "
                      "frames that are not executing. Use !0namespace "
                      "and then try again")
                return
            if magicstring[:6] == "!until":
                command = magicstring[7:]
            elif magicstring[:2] == "!u":
                command = magicstring[3:]
            # this try block sets stepping to line if argument was int
            try:
                cls.until_line = int(command)
            except ValueError:  # argument was not linenumber
                pass
            else:
                return  # argument was linenumber. end
            # this block sets stepping to expressions
            try:
                eval(command) # check that the condition is valid
            except SyntaxError:
                print("'" + command + "'", "is not expression or line")
            except NameError:
                # nameError might happen in this namespace
                # but it might be valid condition somewhere else
                cls.until_expr = command
            else:
                cls.until_expr = command
        elif magicstring in ("!traceback", "!t"):
            print()
            for call in traceback.format_stack()[:-2]:
                print(call)
        elif magicstring in ("!where", "!w"):
            current_line = sys._getframe(cls.scope+2).f_lineno
            path = inspect.getsourcefile(sys._getframe(cls.scope+2))
            # just assume utf8 encoding. good enough compability.
            with open(path, "r", encoding="utf-8") as file:
                source = file.read().splitlines()
            print()
            for line_no, line in enumerate(source, 1):  # fix off by 1
                if current_line == line_no:
                    # show where we actually are. tracing happens
                    # between the source lines
                    print("--->")
                # +0.6 so rounding shows even amount of lines, not odd
                if abs(line_no + 0.6 - current_line) <= 5:
                    print("   ", line_no, line)
            print()
        elif magicstring in ("!locals", "!l"):
            # normal locals() cant be used here. it displays wrong scope
            # so frame is used instead
            frame = sys._getframe(cls.scope+2)
            print()
            try:
                # get lenght of longest var name
                max_pad = len(max(frame.f_locals.keys(), key=len))
            except ValueError: # there are no keys
                return
            for name, value in frame.f_locals.items():
                pad = (max_pad-len(name))*" "
                print("   ", name + pad, "=", value)
            print()
        elif magicstring in ("!globals", "!g"):
            # normal globals() cant be used here, displays wrong scope
            # so frame is used instead
            frame = sys._getframe(cls.scope+2)
            print()
            try:
                # get lenght of longest var name
                max_pad = len(max(frame.f_globals.keys(), key=len))
            except ValueError: # there are no keys
                return
            for name, value in frame.f_globals.items():
                pad = (max_pad-len(name))*" "
                print("   ", name + pad, "=", value)
            print()
        elif magicstring in ("!namespace", "!n"):
            print(sys._getframe(cls.scope+2).f_code.co_name)
        elif magicstring in ("!+namespace", "!+"):
            try:
                # +2 like elsewhere to escape seapie. +1 for lookahead
                sys._getframe(cls.scope+2+1)
            except ValueError:
                print("Call stack is not deep enough")
            else:
                cls.scope += 1
        elif magicstring in ("!-namespace", "!-"):
            if cls.scope == 0:
                print("You are at the top of stack (seapie excluded)")
            else:
                cls.scope -= 1
        elif magicstring in ("!0namespace", "!0"):
            cls.scope = 0
        elif (magicstring[:6] in ("!code ", "!code")
              or magicstring[:3] in ("!c ", "!c")):
            if magicstring[:6] == "!code ":
                argument = magicstring[6:]
            if magicstring[:3] == "!c ":
                argument = magicstring[3:]
            try:
                # this is unsafe eval operation
                frame = sys._getframe(cls.scope+2)
                source = inspect.getsource(
                         eval(argument, frame.f_globals, frame.f_locals)
                         )
            except:
                print(traceback.format_exc().splitlines()[-1])
            else:
                print()
                for line in source.splitlines():
                    print("    " + line.rstrip())
                print()
        else:  # the final fallback
            print("Unknown magic command!")


# the below lines are supposed to be run at import time. they are
# intentionally outside of any sort of if __name__ == "__main__" block

seapie = Seapie.seapie
true_exec = Seapie.true_exec

try:  # add ps1 if it does not exist already
    sys.ps1
except AttributeError:
    sys.ps1 = ">>> "
try: # add ps2 if it does not exist already
   sys.ps2
except AttributeError:
    sys.ps2 = "... "


if __name__ == "__main__":
    print("You probably should import this file instead of running it")
    seapie(["!help"])