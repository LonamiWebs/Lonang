from .statement import Statement
from utils import parseint


def add(c, m):
    """Addition statement. For instance:
        dx += cx
    """
    if parseint(m.group(2)) == 1:
        c.add_code(f'inc {m.group(1)}')
    else:
        c.add_code(f'add {m.group(1)}, {m.group(2)}')


add_statement = Statement(
    r'(VAR) \+= (INM)',
    add
)
