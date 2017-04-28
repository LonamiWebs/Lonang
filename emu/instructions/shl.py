from .instruction import paramcount


@paramcount(2)
def shl(m, params):
    """SHL dst, src"""
    # TODO Only cx or inmediate should be valid
    dst, src = params
    m[dst] <<= m[src]
    m.update_flags(m[dst], size=m.sizeof(dst))
