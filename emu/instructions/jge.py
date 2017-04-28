from .instruction import paramcount


@paramcount(1)
def jge(m, params):
    """JGE label"""
    if m['sf'] == m['of']:
        label = params[0]
        m['ip'] = m.labels[label]
