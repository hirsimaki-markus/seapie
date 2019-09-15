_Have you ever wanted to escape current scope to modify enclosing variables?_\
_Have you ever wanted to debug something without bothering to learn how to use a real debugger?_\
_Have you ever wanted to just open the normal interactive prompt inside of your program and then continue?_\

__Seapie can do that__

<img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/SEAPIE.png" width="70" height="70"/>

# SEAPIE 1.0

```SEAPIE``` stands for Scope Escaping Arbitrary Python Injection Executor

## Example

Just add call to seapie() anywhere and magically modify your program's current state in interactive prompt

```ruby
C:\Users\Me\SEAPIE> type demo.py
from seapie import Seapie as seapie
def test():
    seapie(1, "cant_modify_me = 'i can actually'")
    # you could use 'seapie()' for interactive mode instead of arguments
def parent_of_test():
    cant_modify_me = "x"
    test()
    print(you_cant_modify_me_from_test_func)
 parent_of_test()

C:\Users\Me\SEAPIE> python demo.py
i can actually
```
## Todo
* No idea actually. Send me email if you have suggestions

## Known issues

These are rather technical and should not bother you unless you introduce _completely new_ objects in seapie and want
these changes to actually persist into your program outside of the calling function scope. In global scope this doesn't happen
nor does it happen for any objects that already have their name in symbol table (read: anything you can call somehow).

Assinging completely new non-global objects via seapie prompt works but calling said object that has only been defined in
seapie prompt will result in NameError. This happens due to python optimizing local namespaces and as far as I know this
cannot be solved within the scope of this project. Email me if you happen to have ideas about how to do it.

There are few ways to circumvent this in your main program:
* Assing, import and define your objects beforehand
* Assing placeholder to your objects beforehand
* Reassing object to itself in main program to update symbol table: x = locals()["x"]
* Use exec() in main program instead of directly calling to avoid optimization. Instead of calling x do: exec("x")

## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/unlisence.png" width="12" height="12"/> by Markus Hirsimäki in 2019
