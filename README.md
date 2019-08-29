<img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/SEAPIE.png" width="70" height="70"/>

# SEAPIE

``SEAPIE`` stands for ``Scope Escaping Arbitrary Python Injection Executor``

You can call ``seapie()`` _anywhere_ in your code to open python interpeter like console that can edit global, local and any
other variable available in _any_ scope that is in the current call stack.

## Example

```
>>> import seapie
>>>
>>> def test():
...     x = 1
...     seapie.seapie()
...     print("new value of x is", x)
...
>>> test()
SEAPIE v0.4 type !help for SEAPIE help
>>> x = 2 # anow we change the value of x in scope of test()
>>> !exit
new value of x is 2
```

## Known issues

Assinging new variables via seapie only works but calling variable that has only been defined in seapie prompt will result in
NameError. You can try circumventing this by calling and parsing locals() to get your newly and hackily assinged variable name
and using exec() instead of directly calling the variable.

But you most likely shouldn't structure your code to call variables that have been defined via interactive propmt only.


## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/unlisence.png" width="12" height="12"/> by Markus Hirsimäki in 2019
