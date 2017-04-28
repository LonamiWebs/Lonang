from .instruction import paramcount


@paramcount(2)
def test(m, params):
    """TEST op1, op2"""
    a, b = params
    m.update_flags(m[a] & m[b], size=max(m.sizeof(a), m.sizeof(b)))
