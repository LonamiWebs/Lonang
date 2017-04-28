from .instruction import paramcount


@paramcount(1)
def call(m, params):
    """CALL label"""
    label = params[0]
    m.push(m['ip'])
    m['ip'] = m.labels[label]
