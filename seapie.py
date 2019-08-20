import sys
import ctypes
import codeop

def seapie(scope=1):
    """Scope Escaping Arbitrary Python Injection Executor"""
    # https://www.python.org/dev/peps/pep-0558/
    # https://faster-cpython.readthedocs.io/mutable.html
    # https://docs.python.org/3/library/codeop.html#codeop.compile_command
    # https://docs.python.org/3/library/code.html#module-code

    def prompt():
            accumulator = ""
            while True:
                if not accumulator: raw_text = input(">>> ")
                else:               raw_text = input("... ")
                # next two lines catch magic values when they are entered alone
                if accumulator == "":
                    if raw_text in ("quit", "exit", "exit()"): return "!EXIT"
                accumulator += "\n"+raw_text
                # add newline to as input doesnt read it. this will add extra
                # newline at start
                result = codeop.compile_command(accumulator)
                if result != None: break
            return accumulator[1:] # cut extra newline at start
    while True:
        frame = sys._getframe(1)
        locals().update(frame.f_locals)
        codeblock = prompt()
        if codeblock == "!EXIT":
            break # this block allows reacting to magic values
        try:
            print(eval(codeblock)) # print all expressions
            print("evaled")
        except SyntaxError:        # and pass statements
            exec(codeblock)
        #exec(print(x))
        #print(x)
        
        local = dict(locals())
        for i in ("injection", "local", "frame", "__doc__", "prompt", "codeblock"):
            try:
                local.pop(i)
            except KeyError: # remove local variables if they exist to avoid
                             # polluting namespace
                pass
        #print("====")
        #for i in dict(frame.f_locals):
        #    print("before", i)
        #print("====")
        #x
        frame.f_locals.update(local)
        #frame.f_locals # EXISTING LOCAL VARIABLES MUST NOT BE UPDATED AFTER THIS CALL
        # NOR SHOULD FRAME.F_LOCALS BE CALLED AGAIN FOR ANY PURPOSE
        #print(x)
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame),ctypes.c_int(1))
