from .instruction import paramcount


@paramcount(1)
def dec(m, params):
    """DEC dst"""
    dst = params[0]
    access_set(dst, alu_operate(dst, None, lambda d, s: d - 1))
