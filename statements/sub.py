from .statement import Statement
from .utils import parseint


def sub(c, m):
    """Subtraction statement. For instance:
        ax -= bx
    """
    if parseint(m.group(2)) == 1:
        c.add_code(f'dec {m.group(1)}')
    else:
        c.add_code(f'sub {m.group(1)}, {m.group(2)}')


sub_statement = Statement(
    r'(\w+) -= (VALUE)',
    sub
)
