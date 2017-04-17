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
    #
    # If a a parameter is assigned to a function parameter,
    # and this function parameter appears later as as a caller
    # parameter, we need to push it to the stack or we'd lose it:
    #
    #   function f(ax, bx) {
    #   }
    #
    #   f(bx, ax)
    #
    # Also append as many times as we find it, in case
    # we use the same argument (e.g., 'bx, ax, ax')
    pushed = []
    for i in range(len(params)):
        caller_p = params[i]
        func_p = function.params[i]

        found = False
        for j in range(i+1, len(params)):
            if func_p == params[j]:
                found = True
                pushed.append(params[j])
                c.add_code(f'push {params[j]}')

        # If the parameter we've pushed matches the one being used,
        # use the pushed one since it contains the right value
        if pushed and pushed[-1] == caller_p:
            # Pop to assign the value to the function parameter
            c.add_code(f'pop {func_p}')
            pushed.pop()
        else:
            c.add_code(helperassign(func_p, caller_p))

    # TODO This won't be able to push 8 bits, thus neither pop them,
    #      whereas the helperassign() would, in theory, support this
    #
    # Parameters are ready, call the function
    c.add_code(f'call {function.name}')

    # Copy the result back if required
    if assigned_to is not None:
        c.add_code(helperassign(assigned_to, function.returns))


functioncall_statement = Statement(
    r'(?:(\w+) = )?(\w+)\(([\w, ]+)\)',
    functioncall
)
