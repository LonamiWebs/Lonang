from .statement import Statement
from utils import parseint, helperoperate
from operands import Operand


def add(c, m):
    """Addition statement. For instance:
        dx += cx
    """
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(2))
    if src.value == 1:
        c.add_code(f'inc {dst}')
    else:
        helperoperate(c, 'add', dst, src)


add_statement = Statement(
    r'(VAR) \+= (INM)',
    add
)
