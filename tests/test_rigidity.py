import unittest
import tempfile
import csv
import os

try:
    from unittest import mock
except ImportError:
    import mock

import rigidity
import rigidity.rules
from rigidity import rules

DATA_DIR = os.path.join(os.path.split(__file__)[0], 'data')


class TestRigidity(unittest.TestCase):
    '''
    Test the behavior of the Rigidity class and its ability to wrap the
    csv interfaces.
    '''

    def test_validate_no_rules(self):
        '''
        Test that the validate() method does not change the data if no
        rules are provided.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()), [[], []])

        data1 = [['a', 'b'], ['c', 'd']]
        self.assertEqual(r.validate(data1), data1)

    def test_validate_read_no_rules(self):
        '''
        Test that the validate_read() method does not change the data
        if no rules are provided.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()), [[], []])

        data1 = [['a', 'b'], ['c', 'd']]
        self.assertEqual(r.validate_read(data1), data1)

    def test_validate_write_no_rules(self):
        '''
        Test that the validate_write() method does not change the data
        if no rules are provided.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()), [[], []])

        data1 = [['a', 'b'], ['c', 'd']]
        self.assertEqual(r.validate_write(data1), data1)

    def test_validate_dict_no_rules(self):
        '''
        Test that the validate method works correctly on Dict rows when
        the rules Dict is empty.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()),
                              {'a': [], 'b': []})
        data1 = {'a': 'hello', 'b': 'world'}
        self.assertDictEqual(r.validate(data1), data1)

    def test_validate_dict_read_no_rules(self):
        '''
        Test that the validate_read() method works correctly on Dict
        rows when the rules Dict is empty.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()),
                              {'a': [], 'b': []})
        data1 = {'a': 'hello', 'b': 'world'}
        self.assertDictEqual(r.validate_read(data1), data1)

    def test_validate_dict_write_no_rules(self):
        '''
        Test that the validate_write() method works correctly on Dict
        rows when the rules Dict is empty.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()),
                              {'a': [], 'b': []})
        data1 = {'a': 'hello', 'b': 'world'}
        self.assertDictEqual(r.validate_write(data1), data1)

    def test_writeheader(self):
        '''
        Test that the writehader() method on a CSVWriter is called when
        Rigidity's csvheader() is called.
        '''
        writer = mock.MagicMock()

        r = rigidity.Rigidity(writer, [])
        r.writeheader()
        writer.writeheader.assert_called_once_with()

    def test_writerow(self):
        '''
        Test that the writerow method calls the writerow method of the
        CSVWriter object with validated/corrected data.
        '''
        # Test without rules
        writer = mock.MagicMock()
        r = rigidity.Rigidity(writer, [[], []])
        r.writerow(('hello', 'world'))
        writer.writerow.assert_called_with(['hello', 'world'])
        r.writerow([1, 2])
        writer.writerow.assert_called_with([1, 2])

        # Test with rules
        writer = mock.MagicMock()
        r = rigidity.Rigidity(writer, [[rigidity.rules.Drop()],
                                       [rigidity.rules.Drop()]])
        r.writerow(('hello', 'world'))
        writer.writerow.assert_called_with(['', ''])
        r.writerow([1, 2])
        writer.writerow.assert_called_with(['', ''])

    def test_writerows(self):
        '''
        Write rows to a temporary file with rules.
        '''
        with tempfile.TemporaryFile(mode='w') as csvfile:
            r = rigidity.Rigidity(csv.writer(csvfile))
            r.writerows([['a', 'b'], ['c', 'd']])

    def test___getattr___invalid_attribute(self):
        r = rigidity.Rigidity(None, [[], []])
        self.assertRaises(AttributeError, getattr, r, 'does_not_exist')

    def test___delattr___invalid_attribute(self):
        r = rigidity.Rigidity(None, [[], []])
        self.assertRaises(AttributeError, delattr, r, 'does_not_exist')

    # Tests with actual data
    def test_data_simple_read(self):
        '''
        Perform a read of an actual CSV file with rules.
        '''
        DATA_FILE = 'data_0001.csv'

        rules = [
            [rigidity.rules.Strip()],
            [rigidity.rules.Strip()]
        ]
        with open(os.path.join(DATA_DIR, DATA_FILE)) as csvfile:
            r = rigidity.Rigidity(csv.reader(csvfile), rules)
            for row in r:
                self.assertEqual(row[0], row[0].strip())
                self.assertEqual(row[1], row[1].strip())

    def test___delattr___reader_attribute(self):
        '''
        Test that the __delattr__ method will attempt to delete from
        the CSVReader or CSVWriter object when it has an attribute.

        In this case, the deletion should cause an AttributeError
        because the attribute cannot be deleted.
        '''
        DATA_FILE = 'data_0001.csv'

        with open(os.path.join(DATA_DIR, DATA_FILE)) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['a', 'b'])
            assert hasattr(reader, 'fieldnames')
            r = rigidity.Rigidity(reader)
            self.assertRaises(AttributeError, delattr, r, 'fieldnames')

    def test___next__(self):
        '''
        Test that the __next__ method returns the next row,
        post-validation and post-correction.
        '''
        DATA_FILE = 'data_0001.csv'

        rules = [
            [rigidity.rules.Strip()],
            [rigidity.rules.Strip()]
        ]
        with open(os.path.join(DATA_DIR, DATA_FILE)) as csvfile:
            r = rigidity.Rigidity(csv.reader(csvfile), rules)
            self.assertEqual(next(r), ['hello', 'world'])
            self.assertEqual(next(r), ['things', 'great'])


class TestRigidityDropRow(unittest.TestCase):
    '''
    Test that the Rigidity class handles a DropRow exception correctly.
    '''
    def test_writerow(self):
        writer = mock.MagicMock()
        r_rules = [[rules.Integer(action=rules.Integer.ACTION_DROPROW)]]
        r = rigidity.Rigidity(writer, r_rules)
        r.writerow(['a'])
        self.assertFalse(writer.writerow.called)
