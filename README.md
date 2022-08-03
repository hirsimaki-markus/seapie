_Have you ever wanted to just open the normal interactive prompt inside of your program and then continue?_\
_Have you ever wanted to debug something without ton of print()s but builtin debugger seems too clumsy?_

_Me too. I also got solution for it below._

<img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/SEAPIE.png" width="100" height="100"/>

# SEAPIE 2.0.1

<!-- generated with shields.io. colors: informational and brightgreen and lightgrey -->
<img src="./images/downloads.svg"> <img src="./images/dependencies.svg"> <img src="./images/license.svg"> <img src="./images/size.svg"> <img src="./images/first-release.svg"> <img src="./images/implementation.svg"> <img src="./images/python-ver.svg"> <img src="./images/version.svg">


```SEAPIE``` stands for Scope Escaping Arbitrary Python Injection Executor


## Installation
* Platform independent. Only requirement is CPython api. If you don't know what this is everything should likely work out of the box
* ```pip3 install seapie```
* or ```pip3 install https://github.com/hirsimaki-markus/SEAPIE/archive/master.zip```
* or clone master, cd master, and ```pip3 install .```
* and to uninstall ```pip3 uninstall seapie```


## Features
A picture tells more than thousands words. Internal !help shown below
![](https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/seapiehelp.png)

```import seapie;seapie.true_exec()``` is provided as interface to autoexecute of version 1.2


## Examples
* Start tracing or to just open interactive prompt: ```from seapie import seapie;seapie()``` and maybe enter ```!help```
* Breakpoint your currently onging tracing: step until next ```seapie()``` by using ```!run``` or whatever suits you
* Autoexecute stuff when opening the prompt: ```seapie(["print(123)", "!step", "!verbose", "!until 420"])```
![](https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/seapiegif.gif)


## Todo
* Fix know issues
* Add check for console width to make prettyprinting easier
* Add exit banner/message
* Create decorator for autotracing and excepting functions
* Test how seapie works in multithreaded and multiprocessing programs
* Remove unnecessary features
* Improve on how seapie is imported. Maybe remove singleton requirement.
* Send me email or any message anywhere if you have suggestions
* !r will uselessly stop in loops. Replace with stopping on seapie instead. Problem with catching StopIteration
* Maybe do something useful with ! and !!
* Improve exit and quit, add abilty to just kill the entire thing
* Show all local and globals from all scopes?
* Auo post mortem? Run until crash then trigger seapie?
* History file?
* Make !l and !g display only keys to avoid absolutely flooding the console. Maybe limit print size. Maybe autocomplete from locals. This is stateless unlike history.
* List comprehensions sometimes produce nameerror when referring to local variable. Ipython has the same behaviour, might be unable to fix this. Problem is that new closure is created with list comprehension. A bypass can be achieved with eval("[rules for i in range(3)]", locals()).
    * The problem occurs, for example, when trying to access nonglobal name like this [x[0] for i in x] when x was defined outside of interactive seapie session
    * "The runcode() method of InteractiveInterpreter in code.py uses the 'self.locals' dictionary as the 'globals' parameter of the invoked exec() function. And the do_interact() method of Pdb instantiates InteractiveInterpreter with 'locals' as a merge of the current frame's locals and globals dictionary. This explains why the interact command of pdb evaluates sucessfully the generator expression: the generator function object is evaluated by the interpreter in a frame where 'locals' is NULL (see fast_function() in ceval.c) and 'globals' includes now the debugged frame locals dictionary."
    * So a fix for this problem is to have the default() method of pdb be implemented in the same manner as do_interact() and the runcode() method of InteractiveInterpreter. The attached patch does this.
    * Fix could be for seapie to automagically inject new stuff into the exec namespace when the scope is list comprehension. Or maybe some flag to trigger this.
    * Or maybe do some rewriting and use the builtin code.InteractiveConsole.interact. Actually, scratch that. Cant change parent scope with this.
* Display traceback on seapie startup if there is traceback waiting for try, catch > seapie block
* Overzealous postmortem check (triggers on generator exception and whatnots?) could be causing this behaviour.

## Known issues
* Using arrow keys in seapie prompt might result in keycodes like ```^[[A``` being displayed. This should be fixed by also importing readline along with seapie ``import readline;import seapie;seapie.seapie()``

* ```import seapie;seapie.seapie(["plaintextstring"])``` seems to have side effect of setting ```__doc__``` to ```"plaintextstring"```. This should not be problem as autoexecuting just plain string is useless.

* !w can crash seapie in some situations

* Triggering seapie in list comprehension causes incorrect behaviours. E.g. [seapie.seapie() for i in "a"]. Seems to trigger multiple seapie instances.
* The above applies to all generators probably
* Add step to line number

## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="./images/unlicense.png" width="12" height="12"/> by Markus Hirsimäki in 2019 and 2020
