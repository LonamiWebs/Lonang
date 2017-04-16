from .statement import Statement
from functions import Function


def functiondef(c, m):
    """Function definition. For instance:
        function myMethod(ax) returns dx {
            ; code
        }
    """
    f = Function(m)
    # Ensure that the function doesn't have repeated parameters
    for i in range(len(f.params)):
        for j in range(i + 1, len(f.params)):
            if f.params[i] == f.params[j]:
                raise ValueError(f'Parameter "{f.params[i]}" used twice on '
                                 f'"{f.name}" definition (positions {i+1} '
                                 f'and {j+1})')
    c.begin_function(f)


functiondef_statement = Statement(
    r'function (\w+) \(([\w, ]+)\)(?: returns (\w+))? {',
    functiondef
)
