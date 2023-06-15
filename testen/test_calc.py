import unittest
import calc


class TestCalc(unittest.TestCase):

    def test_add(self):
        self.assertEqual(calc.add(2, 8), 10)
        self.assertEqual(calc.add(-2, 8), 6)
        self.assertEqual(calc.add(2, -8), -6)
        self.assertEqual(calc.add(-2, -8), -10)

    def test_div(self):
        self.assertEqual(calc.div(10, 2), 5)
        self.assertEqual(calc.div(-1, 1), -1)

        self.assertRaises(ZeroDivisionError, calc.div, 10, 0)


if __name__ == '__main__':
    unittest.main()
