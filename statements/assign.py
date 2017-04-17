from .statement import Statement
from utils import helperassign


def assign(c, m):
    """Assignment statement. For instance:
        ax = bx
    """
    c.add_code(helperassign(m.group(1), m.group(2)))


assign_statement = Statement(
    r'(\w+) = (VALUE)',
    assign
)
