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
                eiffel.Return(x + y)
        self.assertEqual(add(1, 2), 3)

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
        message = r"Body block is not defined."
        with self.assertRaisesRegex(SyntaxError, message):
            identity(1)

    def test_ensure(self):
        @eiffel.routine
        def absolute_value(value):
            with eiffel.body:
                result = value
                eiffel.Return(result)
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
        message = r"'eiffel.Return' has not been called."
        with self.assertRaisesRegex(SyntaxError, message):
            identity(1)

    def test_old_inside_function(self):
        @eiffel.routine
        def next_integer(n):
            with eiffel.body:
                result = n + 1
                eiffel.Return(result)
            with eiffel.ensure as old:
                if old is not eiffel.VOID:
                    assert result == old.result + 1

        # Don't check first call
        self.assertEqual(next_integer(1), 2)

        # 3 is 2 + 1
        self.assertEqual(next_integer(2), 3)

        with self.assertRaises(AssertionError):

            # -1 + 1 is 0. But 0 is not 2 + 1
            next_integer(-1)

    def test_old_inside_method(self):
        class Object(eiffel.Class):
            def __init__(self):
                self.value = 0
            @eiffel.routine
            def increment(self):
                with eiffel.body:
                    self.value -= 1
                    eiffel.Return()
                with eiffel.ensure as old:
                    if old is not eiffel.VOID:
                        assert self.value == old.self.value + 1
        obj = Object()

        # Don't check first call
        obj.increment()
        self.assertEqual(obj.value, -1)
        with self.assertRaises(AssertionError):
            obj.increment()

    def test_require_after_body(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                eiffel.Return()
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
                eiffel.Return()
        message = r"Only one 'eiffel.require' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_two_body_blocks(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                eiffel.Return()
            with eiffel.body:
                eiffel.Return()
        message = r"Only one 'eiffel.body' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_two_ensure_blocks(self):
        @eiffel.routine
        def function():
            with eiffel.body:
                eiffel.Return()
            with eiffel.ensure:
                pass
            with eiffel.ensure:
                pass
        message = r"Only one 'eiffel.ensure' block are allowed."
        with self.assertRaisesRegex(SyntaxError, message):
            function()

    def test_return_when_error_in_body_context_manager(self):
        @eiffel.routine
        def error_on_body():
            with eiffel.body:
                raise NameError("name error")
        with self.assertRaises(NameError):
            error_on_body()


if __name__ == "__main__":
    unittest.main()
