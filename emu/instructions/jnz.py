from .instruction import paramcount


@paramcount(1)
def jnz(m, params):
    """JNZ label"""
    if not m['zf']:
        label = params[0]
        m['ip'] = m.labels[label]
