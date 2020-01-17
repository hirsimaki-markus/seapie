"""Seapie is debugger like tool. SEAPIE stands for Scope Escaping Arbitary Python Injection Executor

usage as breakpoint: import seapie;seapie.seapie()

usage as true exec: import seapie;seapie.true_exec(codeblock, scope=0)
    * where codeblock is raw string or compiled code suitable normal exec()
    * where scope states how many scope should be escape. 0 stands for executing in parent scope.

example: import seapie;seapie.true_exec("x=5", scope=0)
    * changes x in calling scope to value of 5.
    * this cant create new variables. they will nameError.
    * scope=1 would change value of x in the scope that encloses the caller of true_exec
"""

import sys
import ctypes
import code
import traceback
import inspect
import codeop


class SingletonException(Exception):
    """helper exception used in case someone tries to initialize seapie instance instead of using the class without instance"""
    pass

class SeapieReplExitException(Exception):
    """raised to close seapie repl"""
    pass

class Seapie:
    """Container class for seapie() and its helper functions."""

    until_expr = None
    until_line = None
    scope = 0

    def __init__(self):
        """Initializes a seapie instance. seapie objects should not be initialized as the class is only a logical collection of functons"""
        # this behaviour is chosen so that code stepping can be implemented easier
        raise SingletonException("The Seapie class is a logical and instanceless singleton! Access the prompt with Seapie.repl() or convenient seapie() that points to Seapie.repl()")

    @classmethod
    def _repl_and_tracelines(cls, frame, event, arg):
        """Main code injector loop"""
        while True:

            #source, start = inspect.getsourcelines(frame)
            #for idx, line in enumerate(source):
            #    print(idx+start, line.rstrip())
            
            # this block autosets condition to step as long as stepstill is valid
            if cls.steptill_condition is None:
                codeblock = cls.single_prompt()
            else:
                #input("tultiin elseen")
                source, start = inspect.getsourcelines(frame)
                #print("source on", source)
                #print("start on", start)
                for idx, line in enumerate(source):
                    #print("looppi")
                    #print(idx+start)
                    if idx+start == 32:
                        cls.steptill_condition = None
                        codeblock = cls.single_prompt()
                        break
                    else:
                        codeblock = "!step"

                # try:
                    # if eval(cls.steptill_condition, frame.f_globals, frame.f_locals):
                        # cls.steptill_condition = None
                        # codeblock = cls.single_prompt()
                    # else:
                        # codeblock = "!step"
                # except NameError: # could not find variable to even try to satisfy condition. skipping.
                    # codeblock = "!step"
                
            # codeblock = cls.single_prompt()
            if isinstance(codeblock, str):  # got magic string
                try:
                    cls.magic_handler(codeblock)
                    continue # magic is handled. get new command
                except SeapieReplExitException: # this is raised in magic handler if the repl should exit. magic handler never returns anything
                    return
                    #return cls._repl_and_tracelines # this might be needed but not really??
            else:
                #try:
                    cls.arbitary_scope_exec(codeblock, 1) # 1 to escape the call to this scope
                #except Exception:  # catch arbitary exceptions from exec
                #    traceback.print_exc()
    @classmethod
    def arbitary_scope_exec(cls, codeblock, scope=0):
        parent = sys._getframe(cls.scope+scope+1)  # frame enclosing seapie() call. +1 escapes this arbitary_executor function itself
        # sys._getframe(scope+1).f_code.co_name # frame contains multiple things like the co_name
        parent_globals = parent.f_globals
        parent_locals = parent.f_locals
        try:
            exec(codeblock, parent_globals, parent_locals)
        except KeyboardInterrupt:  # emulate behaviour of ctrl+c
            print("\nKeyboardInterrupt")
        except Exception:  # catch arbitary exceptions from exec
            traceback.print_exc()
        # the following call forces update to locals()
        # adding new variables is allowed but calling them requires
        # some indirection like using exec() or a placeholder
        # otherwise you will get nameError when calling the variable
        # the magic value 1 stands for ability to introduce new variables. 0 for update-only
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent),
                                                      ctypes.c_int(1))


    @classmethod
    def magic_handler(cls, magicstring):
        """Any magic strings starting with ! are handled here"""
        if magicstring == "!peek":
           print("Next line to be executed is", sys._getframe(cls.scope+2).f_lineno)
        elif magicstring == "!tree":
            print()
            for call in traceback.format_stack()[:-2]:
                print(call)
        elif magicstring == "!locals":
            # normal locals() cant be used here. it displays wrong scope.
            frame = sys._getframe(cls.scope+2)
            print()
            try:
                max_pad = len(max(frame.f_locals.keys(), key=len)) # lenght of longest var name
            except ValueError: # there are no keys
                return
            for name, value in frame.f_locals.items():
                pad = (max_pad-len(name))*" "
                print("   ", name + pad, "=", value)
            print()
        elif magicstring == "!globals":
            # normal globals() cant be used here. it displays wrong scope.
            frame = sys._getframe(cls.scope+2)
            print()
            try:
                max_pad = len(max(frame.f_globals.keys(), key=len)) # lenght of longest var name
            except ValueError: # there are no keys
                return
            for name, value in frame.f_globals.items():
                pad = (max_pad-len(name))*" "
                print("   ", name + pad, "=", value)
            print()
        elif magicstring == "!scope":
            print(sys._getframe(cls.scope+2).f_code.co_name)
        elif magicstring == "!-scope":
            if cls.scope == 0:
                print("You are at the top of stack (seapie is excluded)")
            else:
                cls.scope -= 1
        elif magicstring == "!+scope":
            try:
                sys._getframe(cls.scope+3)  # +2 like elsewhere to escape seapie itself and +1 for lookahead
            except ValueError:
                print("Call stack is not deep enough")
            else:
                cls.scope += 1
        elif magicstring in ("!help", "!h"):
            help = ["",
            "(!h)elp       : Show this info block",
            "(!e)xit       : Close seapie, end tracing and resume main",
            "",
            "(!s)tep       : Execute the next line of source code",
            "(!u)ntil 1234 : Step until line source code line 123",
            "(!u)ntil expr : Step until eval('expr') equals to True",
            "                ├─> e.g.: '!u x==10' or '!u bool(my_var)'",
            "                └─> note: eval is done in executing scope"
            "",
            "(!t)raceback  : Show traceback excluding seapie",
            "(!p)eek       : Show next source lines in current scope",
            "(!l)ocals     : locals() in prettyprinted from",
            "(!g)lobals    : globals() in prettyprinted from",
            "",
            "(!n)amespace  : Show current scope/namespace name",
            "(!+)namespace : Go down in callstack towards global scope",
            "(!-)namespace : Go up in callstack towards local scope",
            "(!0)namespace : Go back to currently executing scope",
            ""]
            for line in help: print("    " + line)
        elif magicstring in ("!exit", "!e"):
            print("Continuing from line", sys._getframe(cls.scope+2).f_lineno)
            sys.settrace(None)
            sys._getframe(cls.scope+2).f_trace = None # set tracing in the calling scope immediately. settrace enables tracing not in the immediate scope
            # stepping is caused by re-entering seapie
            # SeapieReplExitException is used to exit seapie
            # and re-entering wont happen because tracing was unset
            raise SeapieReplExitException
        elif magicstring in ("!step", "!s"):
            if cls.scope != 0:
                print("Stepping is only available in current namespace")
                print("Use '!step force' to bypass this warning")
            else:
                print("Executed line", sys._getframe(cls.scope+2).f_lineno)
                # stepping is caused by re-entering seapie
                # SeapieReplExitException is used to exit seapie
                # and it is re-entering because of tracing
                raise SeapieReplExitException
        elif magicstring in ("!step force"):
            print("Executed line", sys._getframe(cls.scope+2).f_lineno)
            # stepping is caused by re-entering seapie
            # SeapieReplExitException is used to exit seapie
            # and it is re-entering because of tracing
            raise SeapieReplExitException
        elif magicstring[:7] == "!until " or magicstring[:3] == "!u "
            if cls.scope != 0 and magicstring[-6:] != " force":
                print("Stepping is only available in current namespace")
                print("Use '!until expr force' to bypass this warning")
                print("Use '!until 1234 force ' to bypass this warning")
                return
            if magicstring[:7] == "!until "
                command = magicstring[7:]
            if magicstring[:3] == "!u "
                command = magicstring[3:]
            # this try block sets stepping to line
            try:
                cls.until_line = int(command)
            except ValueError: # the command was not intended to be linenumber
                pass
            else:
                return
            # this block sets stepping to expressions
            try
                eval(condition) # check that the condition is valid
            except SyntaxError:
                print("'", condition, "'", "is not expression or lines")
            except NameError:
                cls.until_expr = condition # nameError might happen in this namespace but it might be valid condition somewhere else
            else:
                cls.until_expr = condition
        elif magicstring[:13] == "!until force ":
            pass
        else:
            print("Unknown magic command!")

    @staticmethod
    def single_prompt():
        """Interactive prompt that stays open until it can return single compiled expression/statement or magic string"""
        accumulator = ""
        raw_text = ""
        while True:
            try:
                if not accumulator:  # if on first line of incoming block
                    raw_text = input(str("(S) " + sys.ps1))
                else:  # if on continuing line
                    raw_text = input(str("(S) " + sys.ps2))
            except KeyboardInterrupt:  # emulate behaviour of ctrl+c
                print("\nKeyboardInterrupt")
                accumulator = ""
                continue
            except EOFError:  # emulate behaviour of ctrl+z
                sys.exit(1)
            if accumulator == "" and raw_text.startswith("!"):  # got magic
                return raw_text
            # this block should catch situation where two or more newlines
            # are entered during function definition or other such things
            if raw_text == "":
                try:
                    accumulator = "\n"+accumulator
                    codeop.compile_command(accumulator, "<input>", "single")
                except:  # catch exceptions compiling and reset
                    traceback.print_exc()
                    accumulator = ""
                    continue
            accumulator += "\n"+raw_text  # manually add newline after inputs
            try:
                result = code.compile_command(accumulator)
            except SyntaxError:  # allow incorrect commands to just pass thru
                # return accumulator # tämä muutos alla korjaa lambdat???
                traceback.print_exc()
                accumulator = ""
                continue
            if result is None:
                pass  # incomplete but possibly valid command
            else:
                return result

# THIS BLOCK IS RUN AT IMPORT TIME
# it is INTENTIONALLY not placed inside of """ if name: '__main__': """
# as it is used to initialize the library during import
# and it is used to initialize sys.ps1 and sys.ps2

try:  # enables support for sys.ps1
    sys.ps1
except AttributeError:
    sys.ps1 = ">>> "
try:  # enables support for sys.ps2
   sys.ps2
except AttributeError:
    sys.ps2 = "... "


def trace_calls(frame, event, arg): # triggers on new frame (?) # tämä vastaa tracecallssia. kutsutaan scopn vaihdossa
    # print("Entering scope",  frame.f_code.co_name) make this conditinal?
    return Seapie._repl_and_tracelines # tämö funktio suoritetaan joka kerta mutta tämän funktion sisältä ei lähdetä ?. tämä vastaa tracelinessia kutsutaan joka rivillä


# seapie = Seapie.repl
arbitary_scope_exec = Seapie.arbitary_scope_exec

def seapie():
    sys.settrace(trace_calls)
    sys._getframe(1).f_trace = Seapie._repl_and_tracelines # set tracing in the calling scope immediately. settrace enables tracing not in the immediate scope


BREAKPOINT = True