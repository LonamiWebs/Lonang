from .instruction import paramcount


@paramcount(2)
def xor(m, params):
    """XOR dst, src"""
    dst, src = params
    access_set(dst, alu_operate(dst, src, lambda d, s: d ^ s))
