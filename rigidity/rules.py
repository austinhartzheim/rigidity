import ctypes
import rigidity.errors


class Rule():
    '''
    Base rule class implementing a simple apply() method that returns
    the given data unchanged.
    '''

    def apply(self, value):
        '''
        This is the default method for applying a rule to data. By
        default, the `read()` and `write()` methods will use this
        method to validate and modify data.

        :param value: the data to be validated.
        :returns: the validated and possibly modified value as
          documented by the rule.
        :raises rigidity.errors.DropRow: when the rule wants to
          cancel processing of an entire row, it may do so with
          the DropRow error. This signifies to the
          :class:`rigidity.Rigidity` class that it should
          discontinue processing the row.
        '''
        return value

    def read(self, value):
        '''
        When reading data, it is validated with this method. By
        default, this method calls the `apply()` method of this
        class. However, you may override this method to achieve
        different behavior when reading and writing.

        :param value: the data to be validated.
        :returns: the validated and possibly modified value as
          documented by the rule.
        :raises rigidity.errors.DropRow: when the rule wants to
          cancel processing of an entire row, it may do so with
          the DropRow error. This signifies to the
          :class:`rigidity.Rigidity` class that it should
          discontinue processing the row.
        '''
        return self.apply(value)

    def write(self, value):
        '''
        When writing data, it is validated with this method. By
        default, this method calls the `apply()` method of this
        class. However, you may override this method to achieve
        different behavior when reading and writing.

        :param value: the data to be validated.
        :returns: the validated and possibly modified value as
          documented by the rule.
        :raises rigidity.errors.DropRow: when the rule wants to
          cancel processing of an entire row, it may do so with
          the DropRow error. This signifies to the
          :class:`rigidity.Rigidity` class that it should
          discontinue processing the row.
        '''
        return self.apply(value)


class CapitalizeWords(Rule):
    '''
    Capitalize words in a string. By default, words are detected by
    searching for space, tab, new line, and carriage return characters.
    You may override this setting.

    Also, by default, the first character is capitalized automatically.
    '''
    SEPERATORS = ' \t\n\r'

    def __init__(self, seperators=SEPERATORS, cap_first=True):
        '''
        :param str seperators: capitalize any character following a
          character in this string.
        :param bool cap_first: automatically capitalize the first
          character in the string.
        '''
        self.seperators = seperators
        self.cap_first = cap_first

    def apply(self, value):
        # Create a unicode buffer. These things are mutable!
        buffer = ctypes.create_unicode_buffer(value)

        # If capitalization of the first character is desired, capitalize.
        if self.cap_first:
            buffer[0] = buffer[0].upper()

        # Search for all separators in the string
        for i in range(0, len(buffer) - 1):
            if buffer[i] in self.seperators:
                buffer[i + 1] = buffer[i + 1].upper()

        # Return the modified buffer
        return buffer.value


class Boolean(Rule):
    '''
    Cast a string as a boolean value.
    '''
    #: When invalid data is encountered, raise an exception.
    ACTION_ERROR = 1
    #: When invalid data is encountered, return a set defaut value.
    ACTION_DEFAULT = 2
    #: When invalid data is encountered, drop the row.
    ACTION_DROPROW = 3

    def __init__(self, allow_null=False, action=ACTION_ERROR, default=None):
        '''
        :param action: take the behavior indicated by ACTION_ERROR,
          ACTION_DEFAULT, or ACTION_DROPROW.
        '''
        self.allow_null = allow_null
        self.default = default
        self.action = action

    def apply(self, value):
        lvalue = str(value).lower()
        if lvalue in ('true', 'yes', 't', '1'):
            return True
        elif lvalue in ('false', 'no', 'f', '0'):
            return False
        elif self.allow_null and lvalue in ('null', 'none', ''):
            return None
        else:
            if self.action == self.ACTION_ERROR:
                raise ValueError('Value was not a boolean value')
            elif self.action == self.ACTION_DEFAULT:
                return self.default
            elif self.action == self.ACTION_DROPROW:
                raise rigidity.errors.DropRow()
            else:
                raise ValueError('Value was not a boolean value')


class Bytes(Rule):
    '''
    When reading data, encode it as a bytes object using the given
    encoding. When writing data, decode it using the given encoding.
    '''

    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def read(self, value):
        return value.encode(self.encoding)

    def write(self, value):
        return value.decode(self.encoding)


class Contains(Rule):
    '''
    Check that a string field value contains the string (or all strings
    in a list of strings) passed as a parameter to this rule.
    '''
    def __init__(self, string):
        if isinstance(string, str):
            self.strings = [string]
        elif isinstance(string, (list, tuple)):
            self.strings = string
        else:
            raise ValueError('string must be a string or a lsit')

    def apply(self, value):
        for string in self.strings:
            if string not in value:
                raise ValueError('String "%s" not in value' % string)
        return value


class Integer(Rule):
    '''
    Cast all data to ints or die trying.
    '''
    #: When invalid data is encountered, raise an exception.
    ACTION_ERROR = 1
    #: When invalid data is encountered, return zero.
    ACTION_ZERO = 2
    #: When invalid data is encountered, drop the row.
    ACTION_DROPROW = 3

    def __init__(self, action=ACTION_ERROR):
        '''
        :param action: take the behavior indicated by ACTION_ERROR,
          ACTION_ZERO, or ACTION_DROPROW.
        '''
        self.action = action

    def apply(self, value):
        try:
            return int(value)
        except ValueError as err:
            if self.action == self.ACTION_ERROR:
                raise err
            elif self.action == self.ACTION_ZERO:
                return 0
            elif self.action == self.ACTION_DROPROW:
                raise rigidity.errors.DropRow()
            else:
                raise err


class Float(Rule):
    '''
    Cast all data to floats or die trying.
    '''
    #: When invalid data is encountered, raise an exception.
    ACTION_ERROR = 1
    #: When invalid data is encountered, return zero.
    ACTION_ZERO = 2
    #: When invalid data is encountered, drop the row.
    ACTION_DROPROW = 3

    def __init__(self, action=ACTION_ERROR):
        '''
        :param action: take the behavior indicated by ACTION_ERROR,
          ACTION_ZERO, or ACTION_DROPROW.
        '''
        self.action = action

    def apply(self, value):
        try:
            return float(value)
        except ValueError as err:
            if self.action == self.ACTION_ERROR:
                raise err
            elif self.action == self.ACTION_ZERO:
                return 0.0
            elif self.action == self.ACTION_DROPROW:
                raise rigidity.errors.DropRow()
            else:
                raise err


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
    configurable actions: pass it through unmodified, drop the row,
    or use a default value.
    '''
    #: When no replacement is found, drop the row.
    ACTION_DROPROW = 1
    #: When no replacement is found, return a set default value.
    ACTION_DEFAULT_VALUE = 2
    #: When no replacement is found, allow the original to pass through.
    ACTION_PASSTHROUGH = 3
    #: When no replacement is found, raise an exception.
    ACTION_ERROR = 4
    #: When no replacement is found, return an empty string.
    ACTION_BLANK = 5
    #: .. warning:: ACTION_DROP is deprecated due to the name being similar
    #:    to ACTION_DROPROW. Use ACTION_BLANK instead.
    ACTION_DROP = ACTION_BLANK  # Legacy support for v1.2.0; depreciated

    def __init__(self, replacements={}, missing_action=ACTION_ERROR,
                 default_value=''):
        '''
        :param dict replacements: a mapping between original values
          and replacement values.
        :param missing_action: when a replacement is not found for a
          value, take the behavior specified by the specified value,
          such as ACTION_DROP, ACTION_DEFAULT_VALUE,
          ACTION_PASSTHROUGH, or ACTION_ERROR.
        :param default_value: if ACTION_DEFAULT_VALUE is the missing
          replacement behavior, use this variable as the default
          replacement value.
        '''
        self.replacements = replacements
        self.missing_action = missing_action
        self.default_value = default_value

        if missing_action == self.ACTION_BLANK:
            self.missing_action = self.ACTION_DEFAULT_VALUE
            self.default_value = ''

    def apply(self, value):
        if value in self.replacements:
            return self.replacements[value]
        elif self.missing_action == self.ACTION_DROPROW:
            raise rigidity.errors.DropRow()
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
    Replace a field's value with a static value declared during
    initialization.
    '''
    def __init__(self, value):
        self.static_value = value

    def apply(self, value):
        return self.static_value


class Unique(Rule):
    '''
    Only allow unique values to pass. When a repeated value is found,
    the row may be dropped or an error may be raised.
    '''
    #: When repeat data is encountered, raise an exception.
    ACTION_ERROR = 1
    #: When repeat data is encountered, drop the row.
    ACTION_DROPROW = 2

    def __init__(self, action=ACTION_ERROR):
        '''
        :param action: Accepts either ACTION_ERROR or ACTION_DROPROW as
          the behavior to be performed when a value is not unique.
        '''
        self.action = action
        self.encountered = []

    def apply(self, value):
        if value in self.encountered:
            if self.action == self.ACTION_ERROR:
                raise Exception('Value not unique')
            elif self.action == self.ACTION_DROPROW:
                raise rigidity.errors.DropRow()
            else:
                raise Exception('Value not unique')
        self.encountered.append(value)
        return value


class Drop(Rule):
    '''
    Drop the data in this column, replacing all data with an empty
    string value.
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
    Validate UPC-A barscode numbers to ensure that they are 12 digits.
    Strict validation of the check digit may also be enabled.
    '''

    def __init__(self, strict=False):
        '''
        :param bool strict: If `true`, raise a ValueError if the given
          UPC code fails the check digit validation.
        '''
        self.strict = strict

    def apply(self, value):
        '''
        Cast the value to a string, then check that it is numeric.
        Afterwards, zero-pad the left side to reach the standard length
        of 12 digits.

        :raises ValueError: when strict mode is enabled and the given
          UPC code fails the check digit validation.
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
