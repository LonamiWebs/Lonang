from .instruction import paramcount


@paramcount(1)
def jg(m, params):
    """JG label"""
    if not m['zf'] and m['sf'] == m['of']:
        label = params[0]
        m['ip'] = m.labels[label]
