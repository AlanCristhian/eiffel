# eiffel

A Python Design By Contract (DbC) module.

The goal is that allows to declare constraints on functions and classes
without lambdas. Also meets the full DbC especification, except automatic
generation of documentation. The next example shows the full API and syntax:

```python
import eiffel

class MyClass(eiffel.Class):

    @eiffel.routine
    def function(arguments):
        with eiffel.require:
            PRECONDITION_BLOCK
        try:
            BODY_BLOCK
        finally:
            POSTCONDITION_BLOCK

    def __invariant__(self):
        INVARIANT_BLOCK
```

## Installation

```shell
$ pip install git+https://github.com/AlanCristhian/eiffel.git
```

## Routines

To define a routine you must decorate the function with the `eiffel.routine`
decorator:

```python
import eiffel

@eiffel.routine
def add(x, y):
    return x + y
```

You must always decorate the function with `eiffel.routine` first:

```python
@nth_decorator
...
@third_decorator
@second_decorator
@eiffel.routine
def function():
    pass
```

## Preconditions

A **precondition** is a predicate that must be true just prior to the
execution of a function. For example, in the division the divisor must be
nonzero:

```python
@eiffel.routine
def divide(dividend, divisor):
    with eiffel.require:
        assert divisor != 0
    return dividend/divisor
```

`eiffel.require` does nothing. It only serves to indicate that everything
inside is a precondition. You can skip it if you want:

```python
@eiffel.routine
def divide(dividend, divisor):
    assert divisor != 0
    return dividend/divisor
```

## Postconditions

A **postcondition** is a predicate that must be true just *after* to the
execution of the function. For example, the absolute value of a number is
always positive.

```python
@eiffel.routine
def absolute_value(value):
    try:
       return value if value >= 0 else -value
    finally:
        assert result >= 0
```

Postconditions must be defined inside the `finally` clause. The body of the
function must go inside the `try` statement.

## The `old` object

The `old` object are returned by the `eiffel.get_old` function. This
object is the `eiffel.VOID` constant on *first* function call.

On the *second* call, stores the local namespace of the decorated function with
the values of the *first* call. On the *third* call, have the values of the
*second* call and so on.

For example, the following function should increment the counter. But, as you
can see in the body, the `counter` variable are decremented.

```python
counter = 0

@eiffel.routine
def increment():
    try:
        counter = counter - 1  # counter are decremented
        return counter
    finally:
        old = eiffel.get_old()
        if old is not eiffel.VOID:
            assert result == old.result + 1
```

So, this function do not fails after the first call, but fails after the second
invocation:

```
>>> increment()
-1
>>> increment()
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
        assert result == old.result + 1
AssertionError
```

## Class Invariants

A **class invariant** is a constraint imposed on all *public methods* of the
class. Public method are those that not starts with undersocre (`_`). For
example, the age of a person is always positive:

```python
class Person(eiffel.Class):
    def __init__(self, age):
        self.age = age

    def set_age(self, value):
        self.age = value

    def __invariant__(self):
        assert self.age >= 0
```

To define a class that can check invariants you must create a derived class of
`eiffel.Class`. Then the constranins are defined by the `__invariant__` method.
This method does not take arguments.

```
>> python = Person(age=10)
>> python.set_age(-10)
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    assert self.age >= 0
AssertionError
```

The constraints are checked *after* object initialization, and *after* a method
is called.

## Inheritance

Since `eiffel.Class` is a normal python class, you can handle inheritance as
usual.

## Overriding `__setattr__` and `__delattr__`

if you want to override the `__setattr__` or `__delattr__` method of the
`eiffel.Class` subclasses, you should use `eiffel.__setattr__` and
`eiffel.__delattr__` functions instead `object.__setattr__` and
`object.__delattr__` respectively. Se the example below:

```python
class LogDeleted(eiffel.Class):
    def __init__(self):
        self.value = "value"

    def __delattr__(self, name):
        eiffel.__delattr__(self, name)
        print(f"'{name}' attribute was deleted")
```

```
>>> obj = LogDeleted()
>>> del obj.value
'value' attribute was deleted
```

If you don't use those functions, the class will loose the hability to check
constrains. You can use `super().__setattr__` and `super().__delattr__` if you
want.
