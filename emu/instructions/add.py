from .instruction import paramcount


@paramcount(2)
def add(m, params):
    """ADD dst, src"""
    dst, src = params
    m[dst] += m[src]
    m.update_flags(m[dst], size=m.sizeof(dst))
