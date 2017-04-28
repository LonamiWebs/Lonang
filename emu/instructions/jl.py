from .instruction import paramcount


@paramcount(1)
def jl(m, params):
    """JL label"""
    if flags['sf'] != flags['of']:
        label = params[0]
        registers['ip'] = labels[label]
