# type: ignore

import functools
import unittest
from unittest import mock

import eiffel


global_variable = 0


# Test performed in debug mode
# ============================


@unittest.skipUnless(__debug__, "Assertions ar performed in debug mode only.")
class ClassCaseDebug(unittest.TestCase):
    def test_check_invariants_after_initialization(self):

        class Positive(eiffel.Class):
            def __init__(self, value):
                self.value = value

            def __invariant__(self):
                assert self.value >= 0

        with self.assertRaises(AssertionError):
            Positive(value=-6)

    def test_check_invariants_after_method_call(self):

        class Negative(eiffel.Class):
            def __init__(self, value):
                self.value = value

            def set_value(self, value):
                self.value = value

            def __invariant__(self):
                assert self.value < 0

        n = Negative(value=-7)

        with self.assertRaises(AssertionError):
            n.set_value(+8)

    def test_check_invariant_on_attribute_assignment(self):

        class Object(eiffel.Class):
            def __init__(self):
                self.attribute = 1

            def __invariant__(self):
                assert self.attribute >= 0

        with self.assertRaises(AssertionError):
            Object().attribute = -1

    def test_inheritance(self):

        class Person(eiffel.Class):
            def __init__(self, name):
                self.name = name

            def __invariant__(self):
                assert self.name.istitle()

        class Employee(Person):
            pass

        with self.assertRaises(AssertionError):
            Employee(name="python")

    def test_that_instance_do_not_change_the_class(self):

        class Object(eiffel.Class):
            pass

        obj = Object()
        obj._invariant_enabled = False

        self.assertEqual(Object._invariant_enabled, True)


@unittest.skipUnless(__debug__, "Assertions ar performed in debug mode only.")
class ContextManagersCaseDebug(unittest.TestCase):

    def test_body(self):
        @eiffel.routine
        def add(x, y):
            return x + y

        self.assertEqual(add(1, 2), 3)

    def test_precondition(self):

        @eiffel.routine
        def divide(dividend, divisor):
            with eiffel.require:
                assert divisor != 0
            return dividend/divisor

        with self.assertRaises(AssertionError):
            divide(4, 0)

    def test_postcondition(self):

        @eiffel.routine
        def absolute_value(value):
            try:
                result = value
                return result
            finally:
                assert result >= 0

        with self.assertRaises(AssertionError):
            absolute_value(-5)


@unittest.skipUnless(__debug__, "Assertions ar performed in debug mode only.")
class OldObjectCaseDebug(unittest.TestCase):
    def test_old_without_check_if_is_defined(self):

        @eiffel.routine
        def previous_integer(n):
            try:
                result = n - 1
                return result
            finally:
                assert result == eiffel.old.result + 1

        message = r"'old' has no attributes. Wrap your postconditions " \
                  r"inside an 'if eiffel.old:' statement."

        with self.assertRaisesRegex(ValueError, message):
            previous_integer(2)

    def test_old_after_check_if_is_defined(self):

        @eiffel.routine
        def next_integer(n):
            try:
                result = n + 1
                return result
            finally:
                if eiffel.old:
                    assert result == eiffel.old.result + 1

        # Don't check first call
        self.assertEqual(next_integer(1), 2)

        # 3 is 2 + 1
        self.assertEqual(next_integer(2), 3)
        with self.assertRaises(AssertionError):

            # -1 + 1 is 0. But 0 is not 2 + 1
            next_integer(-1)

    def test_function_no_decorated(self):

        def function():
            if eiffel.old:
                pass

        message = r"'function' function is not decorated " \
                  r"with 'eiffel.routine' decorator."

        with self.assertRaisesRegex(ValueError, message):
            function()

    def test___result___attribute_on_old(self):

        def counter():
            start = -1

            @eiffel.routine
            def count():
                try:
                    nonlocal start
                    start = start + 1
                    return start
                finally:
                    if eiffel.old:
                        assert start == eiffel.old.__result__ + 1

            return count

        count = counter()

        for i in range(10):
            self.assertEqual(i, count())

    def test_different_namespaces(self):
        @eiffel.routine
        def function_1():
            try:
                value = 1
                return value
            finally:
                if eiffel.old:
                    assert eiffel.old.value == 1

        @eiffel.routine
        def function_2():
            try:
                value = 2
                return value
            finally:
                if eiffel.old:
                    function_1()
                    function_1()
                    assert eiffel.old.value == 2
        function_2()
        function_2()


@unittest.skipUnless(__debug__, "Assertions ar performed in debug mode only.")
class __setattr__and__delattr__CaseDebug(unittest.TestCase):

    def test__setattr__method(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __invariant__(self):
                assert self.attr == 1

        my_object = MyClass()

        with self.assertRaises(AssertionError):
            my_object.attr = 2

    def test__delattr__method(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __invariant__(self):
                assert hasattr(self, "attr")

        my_object = MyClass()

        with self.assertRaises(AssertionError):
            del my_object.attr

    def test_eiffel__setattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __setattr__(self, name, attr):
                eiffel.__setattr__(self, name, attr)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        my_object.attr = 1
        my_object.__invariant__.assert_called()

    def test_eiffel__delattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __delattr__(self, name):
                eiffel.__delattr__(self, name)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        del my_object.attr
        my_object.__invariant__.assert_called()

    def test_super__setattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __setattr__(self, name, attr):
                super().__setattr__(name, attr)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        my_object.attr = 1
        my_object.__invariant__.assert_called()

    def test_super__delattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __delattr__(self, name):
                super().__delattr__(name)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        del my_object.attr
        my_object.__invariant__.assert_called()



# Test performed on optimized mode
# ================================


@unittest.skipIf(__debug__, "No assertions performed in optimized mode.")
class ClassCase(unittest.TestCase):
    def test_check_invariants_after_initialization(self):

        class Positive(eiffel.Class):
            def __init__(self, value):
                self.value = value

            def __invariant__(self):
                assert self.value >= 0

        Positive.__invariant__ = mock.MagicMock()
        p = Positive(value=-20)
        p.__invariant__.assert_not_called()

    def test_check_invariants_after_method_call(self):

        class Negative(eiffel.Class):
            def __init__(self, value):
                self.value = value

            def set_value(self, value):
                self.value = value

            def __invariant__(self):
                assert self.value < 0

        Negative.__invariant__ = mock.MagicMock()
        n = Negative(value=-21)
        n.set_value(22)
        n.__invariant__.assert_not_called()

    def test_check_invariant_on_attribute_assignment(self):

        class Object(eiffel.Class):
            def __init__(self):
                self.attribute = 23

            def __invariant__(self):
                assert self.attribute >= 0

        Object.__invariant__ = mock.MagicMock()
        o = Object()
        o.attribute = -24
        o.__invariant__.assert_not_called()

    def test_inheritance(self):

        class Person(eiffel.Class):
            def __init__(self, name):
                self.name = name

            def __invariant__(self):
                assert self.name.istitle()

        class Employee(Person):
            pass

        Employee.__invariant__ = mock.MagicMock()
        e = Employee(name="python")
        e.__invariant__.assert_not_called()


@unittest.skipIf(__debug__, "No assertions performed in optimized mode.")
class ContextManagersCase(unittest.TestCase):

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_body(self):
        @eiffel.routine
        def add(x, y):
            return x + y

        self.assertEqual(add(1, 2), 3)
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_precondition(self):

        @eiffel.routine
        def divide(dividend, divisor):
            with eiffel.require:
                assert divisor != 0
            return dividend/divisor

        with self.assertRaises(ZeroDivisionError):
            divide(4, 0)
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_postcondition(self):

        @eiffel.routine
        def absolute_value(value):
            try:
                result = value
                return result
            finally:
                assert result >= 0

        absolute_value(-5)
        functools.wraps.assert_not_called()


@unittest.skipIf(__debug__, "No assertions performed in optimized mode.")
class OldObjectCase(unittest.TestCase):

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_old_without_check_if_is_defined(self):

        @eiffel.routine
        def previous_integer(n):
            try:
                result = n - 1
                return result
            finally:
                assert result == eiffel.old.result + 1

        previous_integer(2)
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_old_after_check_if_is_defined(self):
        assert False, "False"

        @eiffel.routine
        def next_integer(n):
            try:
                result = n + 1
                return result
            finally:
                if eiffel.old:
                    assert result == eiffel.old.result + 1

        # Don't check first call
        self.assertEqual(next_integer(1), 2)

        # 3 is 2 + 1
        self.assertEqual(next_integer(2), 3)

        # -1 + 1 is 0. But 0 is not 2 + 1
        next_integer(-1)
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_function_no_decorated(self):

        def function():
            if eiffel.old:
                pass

        function()
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test___result___attribute_on_old(self):

        def counter():
            start = -1

            @eiffel.routine
            def count():
                try:
                    nonlocal start
                    start = start + 1
                    return start
                finally:
                    if eiffel.old:
                        # This would fail in debug mode
                        assert start == eiffel.old.__result__ - 1

            return count

        count = counter()

        for i in range(10):
            self.assertEqual(i, count())
        functools.wraps.assert_not_called()

    @mock.patch("functools.wraps", new=mock.Mock())
    def test_different_namespaces(self):
        @eiffel.routine
        def function_1():
            try:
                value = 1
                return value
            finally:
                if eiffel.old:
                    assert eiffel.old.value == 1

        @eiffel.routine
        def function_2():
            try:
                value = 2
                return value
            finally:
                if eiffel.old:
                    function_1()
                    function_1()
                    # This would fail on debug mode
                    assert eiffel.old.value == 1
        function_2()
        function_2()
        functools.wraps.assert_not_called()


@unittest.skipIf(__debug__, "No assertions performed in optimized mode.")
class __setattr__and__delattr__Case(unittest.TestCase):

    def test__setattr__method(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __invariant__(self):
                assert self.attr == 1

        my_object = MyClass()
        my_object.attr = 2

    def test__delattr__method(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __invariant__(self):
                assert hasattr(self, "attr")

        my_object = MyClass()
        del my_object.attr

    def test_eiffel__setattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __setattr__(self, name, attr):
                eiffel.__setattr__(self, name, attr)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        my_object.attr = 1
        my_object.__invariant__.assert_not_called()

    def test_eiffel__delattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __delattr__(self, name):
                eiffel.__delattr__(self, name)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        del my_object.attr
        my_object.__invariant__.assert_not_called()

    def test_super__setattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __setattr__(self, name, attr):
                super().__setattr__(name, attr)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        my_object.attr = 1
        my_object.__invariant__.assert_not_called()

    def test_super__delattr__function(self):
        class MyClass(eiffel.Class):

            def __init__(self):
                self.attr = 1

            def __delattr__(self, name):
                super().__delattr__(name)

        my_object = MyClass()
        my_object.__invariant__ = mock.Mock()
        del my_object.attr
        my_object.__invariant__.assert_not_called()


if __name__ == "__main__":
    unittest.main()
