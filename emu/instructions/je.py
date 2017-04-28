from .instruction import paramcount


@paramcount(1)
def je(m, params):
    """JE label"""
    if m['zf']:
        label = params[0]
        m['ip'] = m.labels[label]
