from .statement import Statement
from utils import helperassign
from operands import Operand


def repeat(c, m):
    """Repeat control flow statement. For instance:
        repeat 10 with cx {
            ; code
        }
    """
    label = c.get_uid(m.group(3))
    labelstart = label + '_s'
    labelend = label + '_e'

    # Initialize our loop counter
    helperassign(c, m.group(2), m.group(1))

    # Sanity check, if 0 don't enter the loop unless we know it's not 0
    # This won't optimize away the case where the value is 0
    count = Operand.parseint(m.group(1))
    if count is None or count <= 0:  # count unknown or zero
        c.add_code([
            f'test {m.group(2)}, {m.group(2)}',
            f'jz {labelend}'
        ])

    # Add the start label so we can jump here
    c.add_code(f'{labelstart}:')

    if m.group(2) == 'cx':
        # We can use 'loop' if using 'cx'
        c.add_pending_code([
            f'loop {labelstart}',
            f'{labelend}:'
        ])
    else:
        c.add_pending_code([
            f'dec {m.group(2)}',
            f'jnz {labelstart}',
            f'{labelend}:'
        ])


repeat_statement = Statement(
    r'repeat  (INM)  with  (VAR) {',
    repeat
)
