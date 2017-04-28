from .instruction import paramcount


@paramcount(1)
def call(m, params):
    """CALL label"""
    label = params[0]
    stack.append(registers['ip'])
    registers['ip'] = labels[label]
