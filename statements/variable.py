from .statement import Statement
from variables import Variable


def variable(c, m):
    """Variable or constant definition. For instance:
        byte little = 42
        short big = 1234
        
        const VALUE = 7
    """
    # TODO Support for vectors (SomeString DB 23 DUP(?))
    # TODO Perform more checks to ensure the value is correct
    c.add_variable(Variable(
        vartype=m.group(1),
        name=m.group(2),
        value=m.group(3)
    ))


variable_statement = Statement(
    r'(byte|short|string|const)  (\w+) = (.+)',
    variable
)
