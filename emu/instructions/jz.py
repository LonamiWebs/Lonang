from .instruction import paramcount


@paramcount(1)
def jz(m, params):
    """JZ label"""
    if m['zf']:
        label = params[0]
        m['ip'] = m.labels[label]
