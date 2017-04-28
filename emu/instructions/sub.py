from .instruction import paramcount


@paramcount(2)
def sub(m, params):
    """SUB dst, src"""
    dst, src = params
    m[dst] -= m[src]
    m.update_flags(m[dst], size=m.sizeof(dst))
