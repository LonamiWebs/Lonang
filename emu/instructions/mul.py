from .instruction import paramcount


@paramcount(1)
def mul(m, params):
    """MUL src"""
    # TODO Set flags
    src = params[0]
    size = m.sizeof(src)
    if size == 8:
        m['ax'] = m['al'] * m[src]
    elif size == 16:
        ax = m['ax']
        result = ax * m[src]
        m['dx'] = result >> 16
        m['ax'] = ax & 0xffff
    else:
        print(f'err: invalid operand size on mul')
        quit()
