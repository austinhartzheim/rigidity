import unittest
import tempfile
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
        r = rigidity.Rigidity(tempfile.TemporaryFile(), [[], []])

        data1 = [['a', 'b'], ['c', 'd']]
        self.assertEqual(r.validate(data1), data1)
