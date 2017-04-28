from .instruction import paramcount


@paramcount(2)
def mov(m, params):
    """MOV dst, src"""
    dst, src = params
    access_set(dst, access_get(src))
