# eiffel

Another Python Design By Contract (DbC) module. The goal is that allows to
declare constraints on functions and classes without decorators or lambdas.

## Installation

```shell
$ pip install git+https://github.com/AlanCristhian/eiffel.git
```

## Functions

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

## Preconditions

A **precondition** is a predicate that must be true just prior to the
execution of a function. For example, in the division the divisor must be
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

## Postconditions

A **postcondition** is a predicate that must be true just *after* to the
execution of the function. For example, the absolute value of a number is
always positive.

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

Since both `eiffel.Routine` and `eiffel.Class` are normal python classes, you
can handle inheritance as usual.

## Undoing changes

If the new object state does not meet the restriction, `eiffel.Class`
restore the state stored in the object. For example, for the `Person` class,
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
