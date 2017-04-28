from .instruction import paramcount


@paramcount(0)
def ret(m, params):
    """RET"""
    registers['ip'] = stack.pop()
