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

    def apply(self, value):
        return value.strip()


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
