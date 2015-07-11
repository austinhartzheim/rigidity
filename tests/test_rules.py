import unittest
import rigidity.rules


class TestInteger(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Integer()

    def test_apply_string_integer(self):
        self.assertEqual(self.rule.apply('3'), 3)


class TestUnique(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Unique()

    def test_apply_unique_data(self):
        for i in range(0, 10):
            self.assertEqual(self.rule.apply(i), i)

    def test_apply_repeat_data(self):
        self.rule.apply(10)
        self.assertRaises(Exception, self.rule.apply, 10)


class TestDrop(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Drop()

    def test_apply_empty_string(self):
        self.assertEqual(self.rule.apply(''), '')

    def test_apply_plain_string(self):
        self.assertEqual(self.rule.apply('hello'), '')
