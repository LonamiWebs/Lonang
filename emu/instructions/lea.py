from .instruction import paramcount


@paramcount(2)
def lea(m, params):
    """LEA dst, src"""
    dst, src = params
    m[dst] = m.get_memory_addr(src)
