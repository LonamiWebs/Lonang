from .instruction import paramcount


@paramcount(1)
def mul(m, params):
    """MUL src"""
    # TODO Set flags
    src = params[0]
    size = access_size(src)
    if size == 8:
        access_set('ax', access_get('al') * access_get(src))
    elif size == 16:
        ax = access_get('ax')
        result = ax * access_get(src)
        access_set('dx', result >> 16)
        access_set('ax', ax & 0xffff)
    else:
        print(f'err: invalid operand size on mul')
        quit()
