from .statement import Statement


def variable(c, m):
    """Variable or constant definition. For instance:
        byte little = 42
        short big = 1234
        
        const VALUE = 7
    """
    # TODO Support for vectors (SomeString DB 23 DUP(?))
    # TODO Perform more checks to ensure the value is correct
    if m.group(1) == 'byte':
        c.add_variable(m.group(2), f'DB {m.group(3)}')

    elif m.group(1) == 'short':
        c.add_variable(m.group(2), f'DW {m.group(3)}')

    elif m.group(1) == 'string':
        # Analyze scape sequences and trim the quotes
        ana = m.group(3).strip('"').encode('ascii').decode('unicode_escape')
        quote_open = False
        result = ''

        for analyzed in ana:
            if ord(analyzed) <= 32:
                # Non-printable
                if quote_open:
                    result += '", '
                    quote_open = False
                result += str(ord(analyzed))
                result += ', '
            else:
                # Printable
                if not quote_open:
                    result += '"'
                    quote_open = True
                result += analyzed

        if quote_open:
            result += '"'

        result += ", '$'"
        # Now we have our resulting string encoded properly
        c.add_variable(m.group(2), f'DB {result}')

    elif m.group(1) == 'const':
        c.add_constant(m.group(2), m.group(3))


variable_statement = Statement(
    r'(byte|short|string|const)  (\w+) = (.+)',
    variable
)
