

class Rule():
    '''
    Base rule class implementing a simple apply() method that returns
    the given data unchanged.
    '''

    def apply(self, value):
        return value


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
