from .instruction import paramcount


@paramcount(1)
def jge(m, params):
    """JGE label"""
    if flags['sf'] == flags['of']:
        label = params[0]
        registers['ip'] = labels[label]
