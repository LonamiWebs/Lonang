from .statement import Statement
from utils import cti, ctoi


def forever(c, m):
    """Forever control flow statement. For instance:
        forever {
            ; code
        }
    """
    label = c.get_uid(m.group(1))
    labelstart = label + '_s'
    labelend = label + '_e'

    c.add_code(f'{labelstart}:')
    c.add_pending_code([
        f'jmp {labelstart}',
        f'{labelend}:'
    ])


forever_statement = Statement(
    r'forever {',
    forever
)
