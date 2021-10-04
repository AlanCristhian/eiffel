# type: ignore

import unittest

import eiffel


global_variable = 0


class ClassSuite(unittest.TestCase):
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


class ContextManagersSuite(unittest.TestCase):

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


class OldObjectSuit(unittest.TestCase):

    def test_old(self):

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


if __name__ == "__main__":
    unittest.main()
