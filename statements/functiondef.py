from .statement import Statement
from functions import Function


def functiondef(c, m):
    """Function definition. For instance:
        function myMethod(ax) returns dx {
            ; code
        }
    """
    c.begin_function(Function(m))


functiondef_statement = Statement(
    r'function (\w+) \(([\w, ]+)\)(?: returns (\w+))? {',
    functiondef
)
