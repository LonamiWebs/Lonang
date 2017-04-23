from .statement import Statement
from variables import Variable
from operands import Operand


def variable(c, m):
    """Variable or constant definition. For instance:
        byte little = 42
        short big = 1234

        byte[5] vector1
        byte[] vector2 = 1, 2, 3, 4, 5

        const VALUE = 7
    """
    # TODO Perform more checks to ensure the value is correct
    vartype = m.group(1)
    vector_size = m.group(2)
    name = m.group(3)
    value = m.group(4)
    if not value:
        value = '?'

    if vector_size is None:
        # Single item variable
        c.add_variable(Variable(
            name=name,
            vartype=vartype,
            value=value
        ))
    else:
        # We have a vector, get the comma-separated values
        values = Operand.get_csv(value)

        # Determine its size (remove '[]' by slicing) if given
        vector_size = vector_size[1:-1].strip()
        if vector_size:
            vector_size = int(vector_size)
        else:
            if value == '?':
                raise ValueError('A list of values must be supplied when '
                                 'no vector size is specified')
            vector_size = len(values)

        c.add_variable(Variable(
            name=name,
            vartype=vartype,
            value=values,
            vector_size=vector_size
        ))

variable_statement = Statement(
    #   Type for the variable        vector   or' '      optional value
    r'(byte|short|string|const)(?: (\[ \d* \]) |  )(VAR)(?: = (.+))?',
    #                                              name
    variable
)
