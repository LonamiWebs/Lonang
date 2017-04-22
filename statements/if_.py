from .statement import Statement
from utils import ctoi


def if_(c, m):
    """If control flow statement. For instance:
        if ax < 5 {
            ; code
        }
    """
    label = c.get_uid(m.group(4))
    c.add_code([
        f'cmp {m.group(1)}, {m.group(3)}',
        f'{ctoi[m.group(2)]} {label}'
    ])
    c.add_pending_code(f'{label}:')


if_statement = Statement(
    r'if  (VAR) ([<>=!]+) (INM) {',
    if_
)
