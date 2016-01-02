

class RigidityException(Exception):
    pass


class DropRow(RigidityException):
    '''
    When a rule raises this error, the row that is being processed is
    dropped from the output.
    '''
    pass
