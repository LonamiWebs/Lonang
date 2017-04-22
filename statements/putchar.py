from .statement import Statement
from utils import helperassign
from operands import Operand


def putchar(c, m):
    """Puts a character on the screen. For instance:
        put char 'L'
        put digit cx
    """
    # TODO Possibly add support for not inlining
    src = Operand(c, m.group(2))

    c.add_code('push ax')

    helperassign(c, 'al' if src.size == 8 else 'ax', src)
    if m.group(1) == 'digit':
        c.add_code("add al, '0'")

    c.add_code([
        'mov ah, 14',
        'int 10h',
        'pop ax'
    ])


putchar_statement = Statement(
    r'put  (char|digit)  (INM)',
    putchar
)
