'''
Rigidity is a simple wrapper to the built-in csv module that allows for
validation and correction of data being read/written from/to CSV files.

This module allows you to easily construct validation and correction
rulesets to be applied automatically while preserving the csv interface.
This allows you to easily upgrade old software to use new, strict rules.
'''

import rigidity.errors
import rigidity.rules as rules


class Rigidity():
    '''
    A wrapper for CSV readers and writers that allows
    '''

    csvobj = None  # Declare here to prevent getattr/setattr recursion

    #: Do not display output at all.
    DISPLAY_NONE = 0
    #: Display simple warnings when ValueError is raised by a rule.
    DISPLAY_SIMPLE = 1

    def __init__(self, csvobj, rules=[], display=DISPLAY_NONE):
        '''
        :param csvfile: a Reader or Writer object from the csv module;
          any calls to this object's methods will be wrapped to perform
          the specified rigidity checks.
        :param rules=[]: a two dimensional list containing rules to
          be applied to columns moving in/out of `csvobj`. The row
          indices in this list match the column in the CSV file the list
          of rules will be applied to.
        :param int display: When an error is thrown, display the row
          and information about which column caused the error.
        '''
        self.csvobj = csvobj
        self.rules = rules
        self.display = display

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
        try:
            self.csvobj.writerow(self.validate_write(row))
        except rigidity.errors.DropRow:
            return

    def writerows(self, rows):
        '''
        Validate and correct the data provided in every row and raise an
        exception if the validation or correction fails.

        .. note::
          Behavior in the case that the data is invalid and cannot be
          repaired is undefined. For example, the implementation may
          choose to write all valid rows up until the error, or it may
          choose to only conduct the write operation after all rows have
          been verified. Do not depend on the presence or absence of any
          of the rows in `rows` in the event that an exception occurs.
        '''
        for row in rows:
            self.writerow(row)


    # New methods, not part of the `csv` interface
    def validate(self, row):
        '''
        .. warning::
           This method is deprecated and will be removed in a future
           release; it is included only to support old code. It will
           not produce consistent results with bi-directional rules.
           You should use :meth:`validate_read` or
           :meth:`validate_write` instead.

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
                if hasattr(rule, 'apply'):
                    value = rule.apply(value)
                else:
                    return rule.read(value)
            row[key] = value

        # Return the updated data
        return row

    def validate_write(self, row):
        '''
        Validate that the row conforms with the specified rules,
        correcting invalid rows where the rule is able to do so.

        If the row is valid or can be made valid through corrections,
        this method will return a row that can be written to the CSV
        file. If the row is invalid and cannot be corrected, then this
        method will raise an exception.

        :param row: a row object that can be passed to a CSVWriter's
          __next__() method.
        '''
        # Ensure mutability - I'm looking at you, tuples!
        if not isinstance(row, (list, dict)):
            row = list(row)

        # Iterate through all keys, updating the data
        for key in self.keys:
            value = row[key]
            for rule in self.rules[key]:
                try:
                    value = rule.write(value)
                except ValueError as err:
                    if self.display == self.DISPLAY_SIMPLE:
                        print('Invalid data encountered in column %s:' % key)
                        print(' -', row)
                        print(' - Error raised by rule:', rule)
                        print('')
                    raise err
            row[key] = value

        # Return the updated data
        return row

    def validate_read(self, row):
        '''
        Validate that the row conforms with the specified rules,
        correcting invalid rows where the rule is able to do so.

        If the row is valid or can be made valid through corrections,
        this method will return a row that can be written to the CSV
        file. If the row is invalid and cannot be corrected, then this
        method will raise an exception.

        :param row: a row object that can be returned from CSVReader's
          readrow() method.
        '''
        # Ensure mutability - I'm looking at you, tuples!
        if not isinstance(row, (list, dict)):
            row = list(row)

        # Iterate through all keys, updating the data
        for key in self.keys:
            value = row[key]
            for rule in self.rules[key]:
                try:
                    value = rule.read(value)
                except ValueError as err:
                    if self.display == self.DISPLAY_SIMPLE:
                        print('Invalid data encountered in column %s:' % key)
                        print(' -', row)
                        print(' - Error raised by rule:', rule)
                        print('')
                    raise err
                except IndexError as err:
                    if self.display == self.DISPLAY_SIMPLE:
                        print('IndexError raised in column %s:' % key)
                        print(' -', row)
                        print(' - Error raised by rule:', rule)
                        print('')
                    raise err
            row[key] = value

        # Return the updated data
        return row

    def skip(self):
        '''
        Return a row, skipping validation. This is useful when you want
        to skip validation of header information.
        '''
        return next(self.csvobj)

    def __iter__(self):
        for row in iter(self.csvobj):
            try:
                yield self.validate_read(row)
            except rigidity.errors.DropRow:
                continue

    def __next__(self):
        '''
        Call the __next__() method on the given CSV object, validate and
        repair the row it returns, raise an exception if the row cannot
        be repaired, and then return the row.
        '''
        try:
            return self.validate_read(next(self.csvobj))
        except rigidity.errors.DropRow:
            return next(self)

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
