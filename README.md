# eiffel

Another Python Design By Contract (DbC) implementation. The goal is that allows
to declare constraints on functions and classes without decorators or lambdas.

## Installation

```shell
$ pip install git+https://github.com/AlanCristhian/eiffel.git
```

## Defining Functions

To define a function you must create a subclass of `eiffel.Routine` class:

```python
import eiffel

class add(eiffel.Routine):
    def do(x, y):
        return x + y
```

The `do` method is the body of the function. Then you can call it as usual:

```
>>> add(1, 2)
3
```

## Specifying Preconditions

A **precondition** is a predicate that must be true just prior to the
execution of the function. For example, in the division the divisor must be
nonzero:

```python
class divide(eiffel.Routine):
    def require(dividend, divisor):
        assert divisor != 0

    def do(dividend, divisor):
        return dividend/divisor
```

Preconditions are defined by the `require` method and are checked *before* a
function is called:

```
>>> divide(1, 0)
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    assert divisor != 0
AssertionError
```

The `require` method will have the exact arguments declared in the `do` method.

## Expressing Postconditions

A **postcondition** is a predicate that must be true just *after* to the
execution of the function. For example, the absolute value of a number is
always greater or equal to zero.

```python
class absolute_value(eiffel.Routine):
    def do(value):
        return value if value >= 0 else -value

    def ensure(result):
        assert result >= 0
```

Postconditions are defined by the `ensure` method and are checked *after* the
function is called. This method always get one argument that is the result of
the function.

## Imposing Invariants

A **invariant** is a predicate that must be true *after* object initialization
and and *after* a method is called. For example, the age of a person is always
positive:

```python
class Person(eiffel.Class):
    def __init__(self, age):
        self.age = age

    def set_age(self, value):
        self.age = value

    def __invariant__(self):
        assert self.age >= 0
```

To define a class that can check invariants you must create a subclass of
`eiffel.Class` class, as seen in the above example. Then the constranints
are defined by the `__invariant__` method. This method does not take arguments.

```
>> Alexandre = Person(age=57)
>> Alexandre.set_age(-10)
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    assert self.age >= 0
AssertionError
```
