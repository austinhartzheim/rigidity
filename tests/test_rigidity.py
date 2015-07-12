import unittest
import unittest.mock
import tempfile
import csv

import rigidity


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
        writer = unittest.mock.MagicMock()

        r = rigidity.Rigidity(writer, [])
        r.writeheader()
        writer.writeheader.assert_called_once_with()
