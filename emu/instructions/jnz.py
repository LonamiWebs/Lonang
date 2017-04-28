from .instruction import paramcount


@paramcount(1)
def jnz(m, params):
    """JNZ label"""
    if not flags['zf']:
        label = params[0]
        registers['ip'] = labels[label]
