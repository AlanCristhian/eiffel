# eiffel

Another Python Design By Contract (DbC) module. The goal is that allows to
declare constraints on functions and classes without decorators or lambdas.
Also meets the full DbC especification, except automatic generation of
documentation.

## Installation

```shell
$ pip install git+https://github.com/AlanCristhian/eiffel.git
```

## General syntax

```python
import eiffel

class MyClass(eiffel.Class):

    @eiffel.routine
    def function(arguments):
        with eiffel.require:
            REQUIRE_BLOCK
        with eiffel.body:
            BODY_BLOCK
            result = "any value"
        with eiffel.ensure as old:
            ENSURE_BLOCK
        return result

    def __invariant__(self):
        INVARIANT_BLOCK
```

## Routine

To define a function you must decorate the function with the `eiffel.routine`
decorator and use the `eiffel.body` context manager:

```python
import eiffel

@eiffel.routine
def add(x, y):
    with eiffel.body:
        result = x + y
    return result
```

You must define the `result` variable and then return it. Then you can call it
function as usual:

```
>>> add(1, 2)
3
```

You must explicity define the value of the result variable, even if your
function does not return nothing. In that case just assign the `None` constant.

If the `result` object is different than the function output, the function
will raise a `ValueError`:

```python
@eiffel.routine
def function():
    with eiffel.body:
        result = 1
    return 2
```

You must always decorate the function with `eiffel.routine` first.

TODO

## Preconditions

A **precondition** is a predicate that must be true just prior to the
execution of a function. For example, in the division the divisor must be
nonzero:

```python
@eiffel.routine
def divide(dividend, divisor):
    with eiffel.require:
        assert divisor != 0
    with eiffel.body:
        result = dividend/divisor
    return result
```

Preconditions must be defined inside the `eiffel.require` context manager
*before* the `eiffel.body` context manager. Then the function fails as
expected:

```
>>> divide(1, 0)
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    assert divisor != 0
AssertionError
```

## Postconditions

A **postcondition** is a predicate that must be true just *after* to the
execution of the function. For example, the absolute value of a number is
always positive.

```python
@eiffel.routine
def absolute_value(value):
    with eiffel.body:
        result = value
    with eiffel.ensure:
        assert result >= 0
    return result
```

Postconditions are defined inside the `eiffel.ensure` context manager. Must be
placed *after* the `eiffel.body` context manager.

## `old` object

TODO

## Statement order

TODO

## Invariants

A **invariant** is a constraint imposed on all *public* methods of the class.
For example, the age of a person is always positive:

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
`eiffel.Class`, as seen in the above example. Then the constranints are defined
by the `__invariant__` method. This method does not take arguments.

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

## Undoing changes

If the new object state does not meet the restriction, `eiffel.Class`
restores the state stored in the object. For example, for the `Person` class,
the `age` property is restored after fail:

```
>>> python = Person(age=10)
>>> python.age = -10
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    assert self.age >= 0
AssertionError
>>> python.age
10
```
