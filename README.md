_Have you ever wanted to debug something without bothering to learn how to use a real debugger?_  
_Seapie opens python prompt when you want to edit or view your program's state during execution and then resume running_

<img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/SEAPIE.png" width="70" height="70"/>

# SEAPIE

```SEAPIE``` stands for Scope Escaping Arbitrary Python Injection Executor

## Example

Just add call to seapie.seapie() anywhere and magically modify your program's current state in current scope

```ruby
>>> import seapie
>>>
>>> def test():
...     x = 1
...     seapie.seapie()
...     print("new value of x is", x)
...
>>> test()
SEAPIE v0.5 type !help for SEAPIE help
>>> x = 2 # anow we change the value of x in scope of test()
>>> !exit
new value of x is 2
```

## Todo
* Implement way to easily change scope inside the prompt
* Add more !magic commands

## Known issues

These are rather technical and should not bother you unless you introduce _completely new_ objects in seapie and want
these changes to actually persist into your program outside of the calling function scope. In global scope this doesn't happen
nor does it happen for any objects that already have their name in symbol table (read: anything you can call somehow).

Assinging completely new non-global objects via seapie prompt works but calling object that has only been defined in
seapie prompt will result in NameError. This happens due to python optimizing local namespaces and as far as I know this
cannot be solved within the scope of this project. Email me if you happen to have ideas about how to do it.

There are few ways to circumvent this in your main program:
* Assing, import and define your objects beforehand
* Assing placeholder to your objects beforehand
* Reassing object to itself in main program to update symbol table: x = locals()["x"]
* Use exec() in main program instead of directly calling to avoid optimization. Instead of calling x do: exec("x")

## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/unlisence.png" width="12" height="12"/> by Markus Hirsimäki in 2019
