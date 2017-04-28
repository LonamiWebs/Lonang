from .instruction import paramcount


@paramcount(1)
def jz(m, params):
    """JZ label"""
    if flags['zf']:
        label = params[0]
        registers['ip'] = labels[label]
