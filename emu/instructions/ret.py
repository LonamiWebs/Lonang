from .instruction import paramcount


@paramcount(0)
def ret(m, params):
    """RET"""
    m['ip'] = m.pop()
