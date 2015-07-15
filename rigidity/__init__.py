'''
Rigidity is a simple wrapper to the built-in csv module that allows for
validation and correction of data being read/written from/to CSV files.

This module allows you to easily construct validation and correction
rulesets to be applied automatically while preserving the csv interface.
This allows you to easily upgrade old software to use new, strict rules.
'''

import csv
import rigidity.rules as rules


class Rigidity():
    '''
    A wrapper for CSV readers and writers that allows
    '''
    # TODO: Investigate of DictReaders and DictWriters can be handled in
    #   the same class or if another class is required.

    csvobj = None  # Declare here to prevent getattr/setattr recursion

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
        self.rules = rules

        if isinstance(rules, dict):
            self.keys = rules.keys()
        else:
            self.keys = range(0, len(rules))

    # Wrapper methods for the `csv` interface
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
        self.csvobj.writerow(self.validate(row))

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

    # New methods, not part of the `csv` interface
    def validate(self, row):
        '''
        Validate that the row conforms with the specified rules,
        correcting invalid rows where the rule is able to do so.

        If the row is valid or can be made valid through corrections,
        this method will return a row that can be written to the CSV
        file. If the row is invalid and cannot be corrected, then this
        method will raise an exception.

        :param row: a row object that can be passed to a CSVWriter's
          writerow() method.
        '''
        # Ensure mutability - I'm looking at you, tuples!
        if not isinstance(row, (list, dict)):
            row = list(row)

        # Iterate through all keys, updating the data
        for key in self.keys:
            value = row[key]
            for rule in self.rules[key]:
                value = rule.apply(value)
            row[key] = value

        # Return the updated data
        return row

    def __iter__(self):
        for row in iter(self.csvobj):
            yield self.validate(row)

    def __next__(self):
        '''
        Call the __next__() method on the given CSV object, validate and
        repair the row it returns, raise an exception if the row cannot
        be repaired, and then return the row.
        '''
        return self.validate(next(self.csvobj))

    def __getattr__(self, name):
        if hasattr(self.csvobj, name):
            return getattr(self.csvobj, name)
        else:
            return super().__getattr__(self, name)

    def __setattr__(self, name, value):
        if hasattr(self.csvobj, name):
            return setattr(self.csvobj, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if hasattr(self.csvobj, name):
            return delattr(self.csvobj, name)
        return super().__delattr__(name)
