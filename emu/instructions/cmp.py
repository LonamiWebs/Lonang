from .instruction import paramcount


@paramcount(2)
def cmp(m, params):
    """CMP op1, op2"""
    a, b = params
    m.update_flags(m[a] - m[b], size=max(m.sizeof(a), m.sizeof(b)))
