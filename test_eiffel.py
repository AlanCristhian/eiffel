import unittest

import eiffel


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

    def test_restore_old_value_if_fail(self):
        class Object(eiffel.Class):
            def __init__(self):
                self.attribute = 1
            def __invariant__(self):
                assert self.attribute >= 0
        obj = Object()
        try:
            obj.attribute = -1
        except AssertionError:
            pass
        self.assertEqual(obj.attribute, 1)

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

    def test_undoing_changes_if_method_fail(self):
        class Object(eiffel.Class):
            def __init__(self):
                self.a = 1
                self.b = 2
            def change(self):
                self.a = 3
                self.b = -4
            def __invariant__(self):
                assert self.a >= 0
                assert self.b >= 0
        obj = Object()
        try:
            obj.change()
        except AssertionError:
            pass
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, 2)

    def test_undoing_changes_if_assignment_fail(self):
        class Object(eiffel.Class):
            def __init__(self):
                self.attribute = 1
            def __invariant__(self):
                assert self.attribute >= 0
        obj = Object()
        try:
            obj.attribute = 2
            obj.attribute = 3
            obj.attribute = 4
            obj.attribute = -1
        except AssertionError:
            pass
        self.assertEqual(obj.attribute, 4)

    def test_undoing_changes_if_last_assignment_fail_inside_method(self):
        class Object(eiffel.Class):
            def __init__(self):
                self.attribute = 1
            def change(self):
                self.attribute = 2
                self.attribute = 3
                self.attribute = 4
                self.attribute = -5
            def __invariant__(self):
                assert self.attribute >= 0
        obj = Object()
        try:
            obj.change()
        except AssertionError:
            pass
        self.assertEqual(obj.attribute, 1)


class ContextManagersSuite(unittest.TestCase):
    def test_undecorated_function(self):
        def function():
            with eiffel.body:
                result = None
        message = r"'function' function is not decorated " \
                   "with 'eiffel.routine' decorator."
        with self.assertRaisesRegex(ValueError, message):
            function()

    def test_no_body_block(self):
        @eiffel.routine
        def function():
            pass
        message = r"Body block is not defined."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_body(self):
        @eiffel.routine
        def add(x, y):
            with eiffel.body:
                result = x + y
            return result
        self.assertEqual(add(1, 2), 3)

    def test_body_without_result_variable(self):
        @eiffel.routine
        def identity(x):
            with eiffel.body:
                return x
        message = r"'result' object is not defined."
        with self.assertRaisesRegex(NameError, message):
            identity(1)

    def test_require(self):
        @eiffel.routine
        def divide(dividend, divisor):
            with eiffel.require:
                assert divisor != 0
            with eiffel.body:
                result = dividend/divisor
            return result
        with self.assertRaises(AssertionError):
            divide(4, 0)

    def test_require_with_result_variable(self):
        @eiffel.routine
        def identity(x):
            with eiffel.require:
                result = x
        message = r"'result' object must be defined inside " \
                   "the 'eiffel.body' context manager."
        with self.assertRaisesRegex(NameError, message):
            identity(1)

    def test_ensure(self):
        @eiffel.routine
        def absolute_value(value):
            with eiffel.body:
                result = value
            with eiffel.ensure:
                assert result >= 0
            return result
        with self.assertRaises(AssertionError):
            absolute_value(-5)

    def test_ensure_without_result_variable(self):
        @eiffel.routine
        def identity(x):
            with eiffel.body:
                x
            with eiffel.ensure:
                assert x == x
        message = r"'result' object is not defined."
        with self.assertRaisesRegex(NameError, message):
            identity(1)

    def test_old_in_ensure(self):
        @eiffel.routine
        def next_integer(n):
            with eiffel.body:
                result = n + 1
            with eiffel.ensure as old:
                if old.result is not eiffel.Void:
                    assert result == old.result + 1
            return result

        # Don't check first call
        self.assertEqual(next_integer(1), 2)

        # 3 is 2 + 1
        self.assertEqual(next_integer(2), 3)

        with self.assertRaises(AssertionError):

            # -1 + 1 is 0. But 0 is not 2 + 1
            next_integer(-1)

    def test_result_var_different_than_function_output(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                result = 1
            return 2
        message = r"'result' object is not equal to function output."
        with self.assertRaisesRegex(ValueError, message):
            function()

    def test_require_after_body(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                result = None
            with eiffel.require:
                pass
        message = r"'eiffel.require' must go before 'eiffel.body'."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_ensure_before_body(self):
        @eiffel.routine
        def function():
            with eiffel.ensure:
                pass
            with eiffel.body:
                result = None
        message = r"'eiffel.ensure' must go after 'eiffel.body'."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_two_require_blocks(self):
        @eiffel.routine
        def function():
            with eiffel.require:
                pass
            with eiffel.require:
                pass
            with eiffel.body:
                result = None
        message = r"Only one 'eiffel.require' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_two_body_blocks(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                result = None
            with eiffel.body:
                result = None
        message = r"Only one 'eiffel.body' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_two_ensure_blocks(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                result = None
            with eiffel.ensure:
                pass
            with eiffel.ensure:
                pass
        message = r"Only one 'eiffel.ensure' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()


if __name__ == "__main__":
    unittest.main()
