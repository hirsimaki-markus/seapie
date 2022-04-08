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
* !r will uselessly stop in loops. Replace with stopping on seapie instead.
* Maybe do something useful with ! and !!


## Known issues
* Using arrow keys in seapie prompt might result in keycodes like ```^[[A``` being displayed. This should be fixed by also importing readline along with seapie ``import readline;import seapie;seapie.seapie()``

* ```import seapie;seapie.seapie(["plaintextstring"])``` seems to have side effect of setting ```__doc__``` to ```"plaintextstring"```. This should not be problem as autoexecuting just plain string is useless.

* !w can crash seapie in some situations


## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="./images/unlicense.png" width="12" height="12"/> by Markus Hirsimäki in 2019 and 2020
