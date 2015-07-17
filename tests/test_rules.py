import unittest
import rigidity.rules


class TestRule(unittest.TestCase):
    '''
    Test that the rule class performs minimal functionality suitable
    for subclasses to use.
    '''
    def setUp(self):
        self.rule = rigidity.rules.Rule()

    def test_apply(self):
        self.assertEqual(self.rule.apply('hello'), 'hello')


class TestCapitalizeWords(unittest.TestCase):

    def test_apply(self):
        '''
        Test normal cases of the apply() method, splitting on the
        default characters.
        '''
        rule = rigidity.rules.CapitalizeWords()
        self.assertEqual(rule.apply('hello there, world'), 'Hello There, World')
        self.assertEqual(rule.apply('hi;\nhow\tare ya '), 'Hi;\nHow\tAre Ya ')

    def test_apply_no_cap_first(self):
        '''
        Test that setting the cap_first parameter to false correctly
        disables capitalization of the first letter.
        '''
        rule = rigidity.rules.CapitalizeWords(cap_first=False)
        self.assertEqual(rule.apply('hello there, world'), 'hello There, World')
        self.assertEqual(rule.apply('hi;\nhow\tare ya '), 'hi;\nHow\tAre Ya ')

    def test_apply_custom_seperators(self):
        '''
        Test that the class respects custom seperator characters.
        '''
        rule = rigidity.rules.CapitalizeWords(seperators=' -')
        self.assertEqual(rule.apply('abc def-hij'), 'Abc Def-Hij')


class TestInteger(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Integer()

    def test_apply_string_integer(self):
        self.assertEqual(self.rule.apply('3'), 3)


class TestFloat(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Float()

    def test_apply_string_float(self):
        self.assertEqual(self.rule.apply('1.23'), 1.23)


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


class TestStrip(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Strip()

    def test_apply_no_whitespace(self):
        self.assertEqual(self.rule.apply('hello'), 'hello')

    def test_apply_with_whitespace(self):
        self.assertEqual(self.rule.apply(' \thi \t'), 'hi')


class TestUpcA(unittest.TestCase):

    def test_apply_nonnumeric_upc(self):
        rule = rigidity.rules.UpcA()
        self.assertRaises(Exception, rule.apply, 'imastring')

    def test_apply_upc_too_long(self):
        rule = rigidity.rules.UpcA()
        invalid_upc = '0000000000000'  # UPC is too long (13 digits)
        self.assertRaises(Exception, rule.apply, invalid_upc)

    def test_apply_strict_invalid_upc(self):
        rule = rigidity.rules.UpcA(strict=True)
        invalid_upc = '000000000001'  # Incorrect check digit
        self.assertRaises(Exception, rule.apply, invalid_upc)

    def test_apply_no_strict_invalid_upc(self):
        rule = rigidity.rules.UpcA(strict=False)
        invalid_upc = '000000000001'  # Incorrect check digit
        self.assertEqual(rule.apply(invalid_upc), invalid_upc)

    def test_apply_valid_upc(self):
        rule = rigidity.rules.UpcA(strict=True)
        valid_upc = '000000000000'
        self.assertEqual(rule.apply(valid_upc), valid_upc)


class TestLower(unittest.TestCase):

    def test_apply(self):
        rule = rigidity.rules.Lower()
        self.assertEqual(rule.apply('HELLO'), 'hello')
        self.assertEqual(rule.apply('123'), '123')


class TestUpper(unittest.TestCase):

    def test_apply(self):
        rule = rigidity.rules.Upper()
        self.assertEqual(rule.apply('hello'), 'HELLO')
        self.assertEqual(rule.apply('123'), '123')
