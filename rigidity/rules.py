

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

