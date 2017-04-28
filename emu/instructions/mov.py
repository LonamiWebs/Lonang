from .instruction import paramcount


@paramcount(2)
def mov(m, params):
    """MOV dst, src"""
    dst, src = params
    m[dst] = m[src]
