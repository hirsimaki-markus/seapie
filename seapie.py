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

    def __init__(self):
        """Initializes a seapie instance. seapie objects should not be initialized as the class is only a logical collection of functons"""
        # this behaviour is chosen so that code stepping can be implemented easier
        raise SingletonException("The Seapie class is a logical and instanceless singleton! Access the prompt with Seapie.repl() or convenient seapie() that points to Seapie.repl()")

    @classmethod
    def _repl_and_tracelines(cls, frame, event, arg):
        """Main code injector loop"""
        while True:
            codeblock = cls.single_prompt()
            if isinstance(codeblock, str):  # got magic string
                try:
                    cls.magic_handler(codeblock)
                    continue # magic is handled. get new command
                except SeapieReplExitException: # this is raised in magic handler if the repl should exit. magic handler never returns anything
                    return cls._repl_and_tracelines
            else:
                try:
                    cls.arbitary_scope_exec(codeblock, 1) # 1 to escape the call to this scope
                except Exception:  # catch arbitary exceptions from exec
                    traceback.print_exc()
    @staticmethod
    def arbitary_scope_exec(codeblock, scope=0):
        parent = sys._getframe(scope+1)  # frame enclosing seapie() call. +1 escapes this arbitary_executor function itself
        # sys._getframe(scope+1).f_code.co_name # frame contains multiple things like the co_name
        parent_globals = parent.f_globals
        parent_locals = parent.f_locals
        exec(codeblock, parent_globals, parent_locals)
        # the following call forces update to locals()
        # adding new variables is allowed but calling them requires
        # some indirection like using exec() or a placeholder
        # otherwise you will get nameError when calling the variable
        # the magic value 1 stands for ability to introduce new variables. 0 for update-only
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent),
                                                      ctypes.c_int(1))


    @staticmethod
    def magic_handler(magicstring):
        """Any magic strings starting with ! are handled here"""
        if magicstring == "!step":
            #print("Executing line", frame.f_lineno)
            print("Executed line", sys._getframe(2).f_lineno)
            raise SeapieReplExitException
        if magicstring == "!exit":
            #print("Executing line", frame.f_lineno)
            print("Continuing from line", sys._getframe(2).f_lineno)
            sys.settrace(None)
            sys._getframe(2).f_trace = None # set tracing in the calling scope immediately. settrace enables tracing not in the immediate scope
            raise SeapieReplExitException
        elif magicstring == "!help":
            print("SEAPIE v1.1 type !help for SEAPIE help\n")
            print("!help    : this message")
            print("!step    : step")
            print("!tree    : view current call stack")
            print("!locals  : prettyprint locals")
            print("!globals : prettyprint globals")
            print("!scope   : display the name of the current scope")
        elif magicstring == "!tree":
            print()
            for call in traceback.format_stack()[:-2]:
                print(call)
        elif magicstring == "!locals":
            # normal locals() cant be used here. it displays wrong scope.
            frame = sys._getframe(2)
            print("Locals of", frame.f_code.co_name)
            try:
                max_pad = len(max(frame.f_locals.keys(), key=len)) # lenght of longest var name
            except ValueError: # there are no keys
                return
            for name, value in frame.f_locals.items():
                pad = (max_pad-len(name))*" "
                print(name + pad, value)
        elif magicstring == "!globals":
            # normal globals() cant be used here. it displays wrong scope.
            frame = sys._getframe(2)
            print("Globals of", frame.f_code.co_name)
            try:
                max_pad = len(max(frame.f_globals.keys(), key=len)) # lenght of longest var name
            except ValueError: # there are no keys
                return
            for name, value in frame.f_globals.items():
                pad = (max_pad-len(name))*" "
                print(name + pad, value)
        elif magicstring == "!scope":
            print(sys._getframe(2).f_code.co_name)
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
    print("Entering scope",  frame.f_code.co_name)
    return Seapie._repl_and_tracelines # tämö funktio suoritetaan joka kerta mutta tämän funktion sisältä ei lähdetä ?. tämä vastaa tracelinessia kutsutaan joka rivillä


# seapie = Seapie.repl
arbitary_scope_exec = Seapie.arbitary_scope_exec

def seapie():
    sys.settrace(trace_calls)
    sys._getframe(1).f_trace = Seapie._repl_and_tracelines # set tracing in the calling scope immediately. settrace enables tracing not in the immediate scope

