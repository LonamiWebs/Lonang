from .statement import Statement
from utils import parseint, helperoperate
from operands import Operand


def sub(c, m):
    """Subtraction statement. For instance:
        ax -= bx
    """
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(2))
    if src.value == 1:
        c.add_code(f'dec {dst}')
    else:
        helperoperate(c, 'sub', dst, src)


sub_statement = Statement(
    r'(VAR) -= (INM)',
    sub
)
