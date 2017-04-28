from .instruction import paramcount


@paramcount(2)
def cmp(m, params):
    """CMP op1, op2"""
    op1, op2 = params
    alu_operate(op1, op2, lambda a, b: a - b)
