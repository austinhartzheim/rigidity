import unittest
import rigidity.rules
from rigidity import rules, errors


class TestRule(unittest.TestCase):
    '''
    Test that the rule class performs minimal functionality suitable
    for subclasses to use.
    '''
    def setUp(self):
        self.rule = rigidity.rules.Rule()

    def test_apply(self):
        self.assertEqual(self.rule.apply('hello'), 'hello')


class TestBoolean(unittest.TestCase):

    def test_apply_string_boolean(self):
        rule = rules.Boolean()
        self.assertTrue(rule.apply('true'))
        self.assertTrue(rule.apply('yes'))
        self.assertTrue(rule.apply('t'))
        self.assertTrue(rule.apply('1'))
        self.assertFalse(rule.apply('false'))
        self.assertFalse(rule.apply('no'))
        self.assertFalse(rule.apply('f'))
        self.assertFalse(rule.apply('0'))
        self.assertRaises(ValueError, rule.apply, 'null')
        self.assertRaises(ValueError, rule.apply, 'none')
        self.assertRaises(ValueError, rule.apply, '')

    def test_apply_invalid_boolean(self):
        rule = rules.Boolean()
        self.assertRaises(ValueError, rule.apply, 'a')

    def test_apply_allow_null(self):
        rule = rules.Boolean(allow_null=True)
        self.assertIs(None, rule.apply('null'))
        self.assertIs(None, rule.apply('none'))
        self.assertIs(None, rule.apply(''))

    def test_apply_action_default(self):
        rule = rules.Boolean(action=rules.Boolean.ACTION_DEFAULT, default='t')
        self.assertEqual('t', rule.apply('a'))

    def test_apply_action_droprow(self):
        rule = rules.Boolean(action=rules.Boolean.ACTION_DROPROW)
        self.assertRaises(errors.DropRow, rule.apply, 'a')

    def test_apply_action_invalid(self):
        rule = rules.Boolean(action=None)
        self.assertRaises(ValueError, rule.apply, 'a')


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


class TestContains(unittest.TestCase):

    def test_apply_single_string(self):
        rule = rigidity.rules.Contains('test')
        self.assertEqual(rule.apply('.test.'), '.test.')
        self.assertRaises(Exception, rule.apply, 'DoesNotContain')

    def test_apply_list(self):
        rule = rigidity.rules.Contains(['1', '2'])
        self.assertEqual(rule.apply('12'), '12')
        self.assertRaises(Exception, rule.apply, '23')

    def test_apply_invalid(self):
        self.assertRaises(Exception, rigidity.rules.Contains, None)


class TestInteger(unittest.TestCase):

    def test_apply_string_integer(self):
        rule = rules.Integer()
        self.assertEqual(rule.apply('3'), 3)

    def test_apply_invalid_integer(self):
        rule = rules.Integer()
        self.assertRaises(Exception, rule.apply, 'a')

    def test_apply_action_zero(self):
        rule = rules.Integer(action=rules.Integer.ACTION_ZERO)
        self.assertEqual(rule.apply('3'), 3)
        self.assertEqual(rule.apply('a'), 0)

    def test_apply_action_droprow(self):
        rule = rules.Integer(action=rules.Integer.ACTION_DROPROW)
        self.assertEqual(rule.apply('3'), 3)
        self.assertRaises(errors.DropRow, rule.apply, 'a')

    def test_apply_action_invalid(self):
        rule = rules.Integer(action=None)
        self.assertRaises(Exception, rule.apply, 'a')


class TestFloat(unittest.TestCase):

    def test_apply_string_float(self):
        rule = rigidity.rules.Float()
        self.assertEqual(rule.apply('1.23'), 1.23)

    def test_apply_invalid_float(self):
        rule = rigidity.rules.Float()
        self.assertRaises(Exception, rule.apply, 'a')

    def tset_apply_action_zero(self):
        rule = rules.Float(action=rules.Float.ACTION_ZERO)
        self.assertEqual(rule.apply('1.23'), 1.23)
        self.assertEqual(rule.apply('a'), 0.0)

    def test_apply_action_droprow(self):
        rule = rules.Float(action=rules.Float.ACTION_DROPROW)
        self.assertEqual(rule.apply('1.23'), 1.23)
        self.assertRaises(errors.DropRow, rule.apply, 'a')

    def test_apply_action_invalid(self):
        rule = rules.Float(action=None)
        self.assertRaises(Exception, rule.apply, 'a')


class TestNoneToEmptyString(unittest.TestCase):

    def test_apply(self):
        rule = rigidity.rules.NoneToEmptyString()
        self.assertEqual(rule.apply(None), '')
        self.assertEqual(rule.apply('hello'), 'hello')


class TestRemoveLinebreaks(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.RemoveLinebreaks()

    def test_apply_ending_linebreak(self):
        self.assertEqual(self.rule.apply('hello\r\n'), 'hello')
        self.assertEqual(self.rule.apply('hi\nworld\n'), 'hi\nworld')

    def test_apply_starting_linebreak(self):
        self.assertEqual(self.rule.apply('\r\nhello'), 'hello')
        self.assertEqual(self.rule.apply('\nhi\nworld'), 'hi\nworld')


class TestReplaceValue(unittest.TestCase):

    def test_apply(self):
        rule = rigidity.rules.ReplaceValue({'hello': 'world'})
        self.assertEqual(rule.apply('hello'), 'world')

    def test_apply_default_raises_exception(self):
        '''
        Test that the rule raises an exception when the value does not
        have a replacement available and the default missing_action
        behavior is being used.
        '''
        rule = rigidity.rules.ReplaceValue()
        self.assertRaises(Exception, rule.apply, 'anystring')

    def test_apply_drop(self):
        '''
        Test that when the missing_action is set to the drop behavior,
        an empty string is returned when the value does not have an
        available replacement.
        '''
        rule = rigidity.rules.ReplaceValue(missing_action=rigidity.rules.ReplaceValue.ACTION_DROP)
        self.assertEqual(rule.apply('anystring'), '')

    def test_apply_default_value(self):
        '''
        Test that when the missing_action is set to the drop behavior,
        an empty string is returned when the value does not have an
        available replacement.
        '''
        default_value = 1234
        rule = rigidity.rules.ReplaceValue(missing_action=rigidity.rules.ReplaceValue.ACTION_DEFAULT_VALUE,
                                           default_value=default_value)
        self.assertEqual(rule.apply('anystring'), default_value)

    def test_apply_passthrough_value(self):
        rule = rigidity.rules.ReplaceValue(missing_action=rigidity.rules.ReplaceValue.ACTION_PASSTHROUGH)
        self.assertEqual(rule.apply('anystring'), 'anystring')
        self.assertEqual(rule.apply(30), 30)

    def test_apply_error(self):
        '''
        Test that when the missing_action is the error behavior, an
        error is raised when the value does not have an available
        replacement.
        '''
        rule = rigidity.rules.ReplaceValue(missing_action=rigidity.rules.ReplaceValue.ACTION_ERROR)
        self.assertRaises(IndexError, rule.apply, 'anystring')
        self.assertRaises(IndexError, rule.apply, 10)

    def test_apply_invalid_missing_action(self):
        '''
        Test that when the missing_action is set to an invalid
        behavior and a value does not have an available replacement,
        an exception is raised.
        '''
        rule = rigidity.rules.ReplaceValue(missing_action=None)
        self.assertRaises(IndexError, rule.apply, 'anystring')
        self.assertRaises(IndexError, rule.apply, 10)


class TestStatic(unittest.TestCase):

    def test_apply(self):
        rule = rigidity.rules.Static('hello world')
        self.assertEqual(rule.apply('strings'), 'hello world')


class TestUnique(unittest.TestCase):

    def test_apply_unique_data(self):
        rule = rigidity.rules.Unique()
        for i in range(0, 10):
            self.assertEqual(rule.apply(i), i)

    def test_apply_repeat_data(self):
        rule = rigidity.rules.Unique()
        rule.apply(10)
        self.assertRaises(Exception, rule.apply, 10)

    def test_apply_action_drop(self):
        rule = rules.Unique(action=rules.Unique.ACTION_DROPROW)
        self.assertEquals(rule.apply('a'), 'a')
        self.assertRaises(errors.DropRow, rule.apply, 'a')

    def test_apply_action_invalid(self):
        rule = rules.Unique(action=None)
        rule.apply('test')
        self.assertRaises(Exception, rule.apply, 'test')


class TestDrop(unittest.TestCase):

    def setUp(self):
        self.rule = rigidity.rules.Drop()

    def test_apply_empty_string(self):
        self.assertEqual(self.rule.apply(''), '')

    def test_apply_plain_string(self):
        self.assertEqual(self.rule.apply('hello'), '')


class TestStrip(unittest.TestCase):

    def test_apply_no_whitespace(self):
        '''
        Test that, under the default configuration, strings without
        beginning or trailing whtiespace are preserved.
        '''
        self.rule = rigidity.rules.Strip()
        self.assertEqual(self.rule.apply('hello'), 'hello')

    def test_apply_with_whitespace(self):
        '''
        Test that, with the default configuration, whitespace is
        removed from the beginning and end of the string.
        '''
        self.rule = rigidity.rules.Strip()
        self.assertEqual(self.rule.apply(' \thi \t'), 'hi')

    def test_apply_custom_chars(self):
        '''
        Test that custom characters are accepted instead of the
        default whitespace characters.
        '''
        self.rule = rigidity.rules.Strip('@!')
        self.assertEqual(self.rule.apply(' hello@!'), ' hello')


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
