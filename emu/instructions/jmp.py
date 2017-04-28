from .instruction import paramcount


@paramcount(1)
def jmp(m, params):
    """JMP label"""
    label = params[0]
    registers['ip'] = labels[label]
