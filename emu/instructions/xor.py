from .instruction import paramcount


@paramcount(2)
def xor(m, params):
    """XOR dst, src"""
    dst, src = params
    m[dst] ^= m[src]
    m.update_flags(m[dst], size=m.sizeof(dst))
