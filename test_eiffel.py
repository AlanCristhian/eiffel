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


if __name__ == "__main__":
    unittest.main()
