from .statement import Statement
from utils import helperassign, get_csv
from functions import Function


def functioncall(c, m):
    """Function call. For instance:
        dx = someMethod(8)
    """
    assigned_to = m.group(1)
    params = get_csv(m.group(3))

    # Find the function
    function = c.find_matching_function(
        name=m.group(2),
        param_count=len(params),
        must_return=assigned_to is not None
    )

    if function is None:
        raise ValueError(
            f'No function called {m.group(2)} with {len(params)} argument(s) exists')

    # We have a function, now copy the parameters if required
    c.add_code(helperassign(function.params, params))

    # Parameters are ready, call the function
    c.add_code(f'call {function.name}')

    # Copy the result back if required
    if assigned_to is not None:
        c.add_code(helperassign(assigned_to, function.returns))


functioncall_statement = Statement(
    r'(?:(\w+) = )?(\w+)\((CSV)\)',
    functioncall
)
