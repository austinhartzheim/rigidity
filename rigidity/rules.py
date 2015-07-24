import ctypes


class Rule():
    '''
    Base rule class implementing a simple apply() method that returns
    the given data unchanged.
    '''

    def apply(self, value):
        return value


class CapitalizeWords(Rule):
    '''
    Capitalize words in a string. By default, words are detected by
    searching for space, tab, new line, and carriage return characters.
    You may override this setting.

    Also, by default, the first character is capitalized automatically.
    '''
    SEPERATORS = ' \t\n\r'

    def __init__(self, seperators=SEPERATORS, cap_first=True):
        self.seperators = seperators
        self.cap_first = cap_first

    def apply(self, value):
        # Create a unicode buffer. These things are mutable!
        buffer = ctypes.create_unicode_buffer(value)

        # If capitalization of the first character is desired, capitalize.
        if self.cap_first:
            buffer[0] = buffer[0].upper()

        # Search for all separators in the string
        for i in range(0, len(buffer)-1):
            if buffer[i] in self.seperators:
                buffer[i+1] = buffer[i+1].upper()

        # Return the modified buffer
        return buffer.value


class Integer(Rule):
    '''
    Cast all data to ints or die trying.
    '''

    def apply(self, value):
        return int(value)


class Float(Rule):
    '''
    Cast all data to floats or die trying.
    '''

    def apply(self, value):
        return float(value)


class NoneToEmptyString(Rule):
    '''
    Replace None values with an empty string. This is useful in cases
    where legacy software uses None to create an empty cell, but your
    other checks require a string.
    '''
    def apply(self, value):
        if value is None:
            return ''
        return value


class RemoveLinebreaks(Rule):
    '''
    Remove linebreaks from the start and end of field values. These can
    sometimes be introduced into files and create problems for humans
    because they are invisible.to human users.
    '''
    def apply(self, value):
        return value.strip('\r\n')


class ReplaceValue(Rule):
    '''
    Check if the value has a specified replacement. If it does, replace
    it with that value. If it does not, take one of the following
    configurable actions: pass it through unmodified, drop the value,
    or use a default value.
    '''
    # These variables are equal; see comment in __init__ about how
    #   ACTION_DROP is implemented by using ACTION_DEFAULT_VALUE.
    ACTION_DROP = 1
    ACTION_DEFAULT_VALUE = 2
    ACTION_PASSTHROUGH = 3
    ACTION_ERROR = 4

    def __init__(self, replacements={}, missing_action=ACTION_ERROR,
                 default_value=''):
        self.replacements = replacements
        self.missing_action = missing_action
        self.default_value = default_value

        # Implement dropping by using a default value of an empty string;
        #   this effectively drops the value.
        if missing_action == self.ACTION_DROP:
            self.missing_action = self.ACTION_DEFAULT_VALUE
            self.default_value = ''

    def apply(self, value):
        if value in self.replacements:
            return self.replacements[value]
        elif self.missing_action == self.ACTION_PASSTHROUGH:
            return value
        elif self.missing_action == self.ACTION_DEFAULT_VALUE:
            return self.default_value
        elif self.missing_action == self.ACTION_ERROR:
            raise IndexError('No replacement for value')
        else:
            raise IndexError('No replacement for value; invalid default action')


class Static(Rule):
    '''
    Replace a field's value with a static value.
    '''
    def __init__(self, value):
        self.static_value = value

    def apply(self, value):
        return self.static_value


class Unique(Rule):
    '''
    Only allow unique fields to pass.
    '''
    def __init__(self):
        self.encountered = []

    def apply(self, value):
        if value in self.encountered:
            raise Exception('Value not unique')
        self.encountered.append(value)
        return value


class Drop(Rule):
    '''
    Drop the data in this column.
    '''

    def apply(self, value):
        return ''


class Strip(Rule):
    '''
    Strip excess white space from the beginning and end of a value.
    '''
    def __init__(self, chars=None):
        if chars:
            self.strip_args = [chars]
        else:
            self.strip_args = []

    def apply(self, value):
        return value.strip(*self.strip_args)


class UpcA(Rule):
    '''
    Validate UPC-A barscode numbers to ensure that they are 12 digits,
    '''

    def __init__(self, strict=False):
        self.strict = strict

    def apply(self, value):
        '''
        Cast the value to a string, then check that it is numeric.
        Afterwards, zero-pad the left side to reach the standard length
        of 12 digits.
        '''
        value = str(value)
        if not value.isdigit():
            raise ValueError('UPC-A code is not numeric.')

        # Some barcodes become truncated by spreadsheet software that
        #   treats the column numericly rather than as a string.
        value = '0' * (12 - len(value)) + value
        if len(value) > 12:
            raise ValueError('UPC-A is longer than 12 digits')

        # Verify the UPC check digit
        if self.strict:
            odd = sum([int(x) for x in value[0:11:2]]) * 3
            even = sum([int(x) for x in value[1:11:2]])
            check = (-1 * (odd + even) % 10)
            if int(value[-1]) != check:
                raise ValueError('UPC-A check digit is incorrect')

        return value


class Lower(Rule):
    '''
    Convert a string value to lower-case.
    '''
    def apply(self, value):
        return value.lower()


class Upper(Rule):
    '''
    Convert a string value to upper-case.
    '''
    def apply(self, value):
        return value.upper()
