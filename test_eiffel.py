import unittest

import eiffel


class RoutineSuite(unittest.TestCase):
    def test_do(self):
        class add(eiffel.Routine):
            def do(x, y):
                return x + y
        self.assertEqual(add(1, 2), 3)

    def test_require(self):
        class divide(eiffel.Routine):
            def require(dividend, divisor):
                assert divisor != 0
            def do(dividend, divisor):
                return dividend/divisor
        with self.assertRaises(AssertionError):
            divide(4, 0)

    def test_ensure(self):
        class absolute_value(eiffel.Routine):
            def ensure(result):
                assert result >= 0
            def do(value):
                return value
        with self.assertRaises(AssertionError):
            absolute_value(-5)

    def test_error_if_do_method_is_not_defined(self):
        message = r"Method 'do' is not defined."
        with self.assertRaisesRegex(NotImplementedError, message):
            class void(eiffel.Routine):
                pass

    def test_inheritance(self):
        class add(eiffel.Routine):
            def require(a, b):
                assert a >= 0 and b >= 0
            def do(a, b):
                return a + b
        class positive_add(add):
            pass
        with self.assertRaises(AssertionError):
            positive_add(-1, 1)

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


if __name__ == "__main__":
    unittest.main()
