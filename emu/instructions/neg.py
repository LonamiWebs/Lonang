from .instruction import paramcount


@paramcount(1)
def neg(m, params):
    """NEG dst"""
    # TODO Perhaps instead these non-sense 'aluoperate' I should have
    #      an "update flags" method instead
    dst = params[0]
    value = m[dst]
    size = access_size(dst)

    power = 2**size
    m[dst] = ((value ^ (power - 1)) + 1) & power - 1

    m.update_flags(m[dst], size=m.sizeof(dst))
