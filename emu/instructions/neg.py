from .instruction import paramcount


@paramcount(1)
def neg(m, params):
    """NEG dst"""
    # TODO Perhaps instead these non-sense 'aluoperate' I should have
    #      an "update flags" method instead
    dst = params[0]
    size = access_size(dst)
    access_set(dst, alu_operate(dst, None, lambda d, s: twocomp(d, size)))
