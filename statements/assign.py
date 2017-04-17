from .statement import Statement
from utils import helperassign, get_csv


def assign(c, m):
    """Assignment statement. For instance:
        ax = bx
        ax, dx = dx, ax
    """
    helperassign(c, m.group(1), m.group(2))


assign_statement = Statement(
    r'(CSV) = (CSV)',
    assign
)
