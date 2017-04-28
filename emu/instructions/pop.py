from .instruction import paramcount


@paramcount(1)
def pop(m, params):
    """POP dst"""
    dst = params[0]
    access_set(dst, stack.pop())
