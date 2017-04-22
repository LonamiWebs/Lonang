from .statement import Statement
from utils import parseint, helperoperate
from operands import Operand

translation = {
    '|': 'or',
    '^': 'xor',
    '&': 'and',
    '+': 'add',
    '-': 'sub'
}

translation1 = {
    '+': 'inc',
    '-': 'dec'
}

def dualoperands(c, m):
    """Operations with two operands statement. For instance:
        ax |= bx  ; Bitwise OR
        dx ^= cx  ; Bitwise XOR
        ax &= bx  ; Bitwise AND
        dx += cx  ; Integer addition
        ax -= bx  ; Integer subtraction
    """
    op = m.group(2)
    dst = Operand(c, m.group(1))
    src = Operand(c, m.group(3))

    if src.value == 1 and op in translation1:
        c.add_code(f'{translation1[op]} {dst}')
    else:
        helperoperate(c, translation[op], dst, src)


dualoperands_statement = Statement(
    r'(VAR) ([|^&+-])= (INM)',
    dualoperands
)
