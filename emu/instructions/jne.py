from .instruction import paramcount


@paramcount(1)
def jne(m, params):
    """JNE label"""
    if not flags['zf']:
        label = params[0]
        registers['ip'] = labels[label]
