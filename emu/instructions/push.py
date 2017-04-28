from .instruction import paramcount


@paramcount(1)
def push(m, params):
    """PUSH src"""
    src = params[0]
    m.push(m[src])
