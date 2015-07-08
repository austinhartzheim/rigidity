'''
RigidCSV is a simple wrapper to the built-in csv module that allows for
validation and correction of data being read/written from/to CSV files.

This module allows you to easily construct validation and correction
rulesets to be applied automatically while preserving the csv interface.
This allows you to easily upgrade old software to use new, strict rules.
'''

import csv


class Rigidity():
    '''
    A wrapper for CSV readers and writers that allows
    '''
    # TODO: Investigate of DictReaders and DictWriters can be handled in
    #   the same class or if another class is required.

    def __init__(self, csvobj, rules=[]):
        '''
        :param csvfile: a Reader or Writer object from the csv module;
          any calls to this object's methods will be wrapped to perform
          the specified rigidity checks.
        :param rules=[]: a two dimensional list containing rules to
          be applied to columns moving in/out of `csvobj`. The row
          indices in this list match the column in the CSV file the list
          of rules will be applied to.
        '''
        self.csvobj = csvobj

    def writeheader(self):
        '''
        Plain pass-through to the given CSV object. It is assumed that
        header information is already valid when the CSV object is
        constructed.
        '''
        self.csvobj.writeheader()

    def writerow(self, row):
        '''
        Validate and correct the data provided in `row` and raise an
        exception if the validation or correction fails. Then, write the
        row to the CSV file.
        '''
        raise NotImplementedError()

    def writerows(self, rows):
        '''
        Validate and correct the data provided in every row and raise an
        exception if the validation or correction fails.

        NOTE::
          Behavior in the case that the data is invalid and cannot be
          repaired is undefined. For example, the implementation may
          choose to write all valid rows up until the error, or it may
          choose to only conduct the write operation after all rows have
          een verified. Do not depend on the presense or absense of any
          of the rows in `rows` in the event that an exception occurs.
        '''
        for row in rows:
            self.writerow(row)

    def __next__(self):
        '''
        Call the __next__() method on the given CSV object, validate and
        repair the row it returns, raise an exception if the row cannot
        be repaired, and then return the row.
        '''
        pass

    def __getattr__(self, name):
        return getattr(self.csvobj, name)

    def __setattr__(self, name, value):
        if hasattr(self.csvobj, name):
            return setattr(self.csvobj, name, value)
        return setattr(self, name, value)

    def __delattr__(self, name):
        if hasattr(self.csvobj, name):
            return delattr(self.csvobj, name)
        return delattr(self, name)
