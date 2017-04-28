from .instruction import paramcount


@paramcount(2)
def shr(m, params):
    """SHR dst, src"""
    # TODO Only cx or inmediate should be valid
    dst, src = params
    m[dst] >>= m[src]
    m.update_flags(m[dst], size=m.sizeof(dst))
