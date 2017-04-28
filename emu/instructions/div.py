from .instruction import paramcount


@paramcount(1)
def div(m, params):
    """DIV src"""
    # TODO Set flags
    src = params[0]
    size = m.sizeof(src)
    if size == 8:
        m['al'], m['ah'] = divmod(m['ax'], m[src])
    elif size == 16:
        dxax = (m['dx'] << 16) | m['ax']
        m['ax'], m['dx'] = divmod(dxax, m[src])
    else:
        print(f'err: invalid operand size on div')
        quit()
