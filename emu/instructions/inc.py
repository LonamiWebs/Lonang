from .instruction import paramcount


@paramcount(1)
def inc(m, params):
    """INC dst"""
    dst = params[0]
    m[dst] += 1
    m.update_flags(m[dst], size=m.sizeof(dst))
