from .statement import Statement
from utils import helperassign, parseint
from builtin_functions import define_set_cursor


def setcursor(c, m):
    """Sets the cursor on screen. For instance:
        setcursor(8, 20)
    """
    # TODO Possibly add support for inlining
    setc = define_set_cursor(c)

    row, col = parseint(m.group(1)), parseint(m.group(2))
    
    # Assertion
    if row is not None and not 0 <= row < 256:
        raise ValueError('The row for setcursor must be between 0 and 255')

    if col is not None and not 0 <= col < 256:
        raise ValueError('The column for setcursor must be between 0 and 255')

    # Assertion passed, save the previous value
    c.add_code(f'push dx')

    # Special case: both integer values known
    if row is not None and col is not None:
        c.add_code(f'mov dx, {(row << 8) | col}')
    else:
        # Need to move manually
        helperassign(c, 'dh', m.group(1))
        helperassign(c, 'dl', m.group(2))

    c.add_code(f'call {setc.name}')
    c.add_code(f'pop dx')


setcursor_statement = Statement(
    r'setcursor \( (INM) , (INM) \)',
    setcursor
)
