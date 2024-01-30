import unittest
from create_release_notes.create_release_notes import to_boolean


class TestToBoolFunction(unittest.TestCase):
    def test_true_values(self):
        self.assertTrue(to_boolean("true"))
        self.assertTrue(to_boolean("t"))
        self.assertTrue(to_boolean("1"))

    def test_false_values(self):
        self.assertFalse(to_boolean("false"))
        self.assertFalse(to_boolean("f"))
        self.assertFalse(to_boolean("0"))

    def test_case_insensitivity(self):
        self.assertTrue(to_boolean("TRUE"))
        self.assertTrue(to_boolean("T"))
        self.assertFalse(to_boolean("FALSE"))
        self.assertFalse(to_boolean("F"))

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            to_boolean("invalid")

        with self.assertRaises(ValueError):
            to_boolean(123)

    def test_already_boolean(self):
        self.assertTrue(to_boolean(True))
        self.assertFalse(to_boolean(False))


if __name__ == "__main__":
    unittest.main()
