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

    def test_validate_dict_no_rules(self):
        '''
        Test that the validate method works correctly on Dict rows when
        the rules Dict is empty.
        '''
        r = rigidity.Rigidity(csv.reader(tempfile.TemporaryFile()),
                              {'a': [], 'b': []})
        data1 = {'a': 'hello', 'b': 'world'}
        self.assertDictEqual(r.validate(data1), data1)

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

    def test___getattr___invalid_attribute(self):
        r = rigidity.Rigidity(mock.MagicMock, [[], []])
        self.assertRaises(AttributeError, getattr, r, 'does_not_exist')

    def test___delattr___invalid_attribute(self):
        r = rigidity.Rigidity(mock.MagicMock, [[], []])
        self.assertRaises(AttributeError, delattr, r, 'does_not_exist')


    # Tests with actual data
    def test_data_simple_read(self):
        '''
        Perform a read of an actual CSV file with rules.
        '''
        rules = [
            [rigidity.rules.Strip()],
            [rigidity.rules.Strip()]
        ]
        with open(os.path.join(DATA_DIR, 'data_0001.csv')) as csvfile:
            r = rigidity.Rigidity(csv.reader(csvfile), rules)
            for row in r:
                self.assertEqual(row[0], row[0].strip())
                self.assertEqual(row[1], row[1].strip())