from .instruction import paramcount


@paramcount(1)
def jg(m, params):
    """JG label"""
    if not flags['zf'] and flags['sf'] == flags['of']:
        label = params[0]
        registers['ip'] = labels[label]
