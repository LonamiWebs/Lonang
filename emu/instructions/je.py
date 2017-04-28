from .instruction import paramcount


@paramcount(1)
def je(m, params):
    """JE label"""
    if flags['zf']:
        label = params[0]
        registers['ip'] = labels[label]
