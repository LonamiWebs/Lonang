from .instruction import paramcount


@paramcount(1)
def jne(m, params):
    """JNE label"""
    if not m['zf']:
        label = params[0]
        m['ip'] = m.labels[label]
