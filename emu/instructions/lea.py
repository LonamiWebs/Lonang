from .instruction import paramcount


@paramcount(2)
def lea(m, params):
    """LEA dst, src"""
    dst, src = params
    idx, _ = memory_nameloc[src]
    access_set(dst, idx)
