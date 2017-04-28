from .instruction import paramcount


@paramcount(1)
def div(m, params):
    """DIV src"""
    # TODO Set flags
    src = params[0]
    size = access_size(src)
    if size == 8:
        al, ah = divmod(access_get('ax'), access_get(src))
        access_set('al', al)
        access_set('ah', ah)
    elif size == 16:
        dxax = (access_get('dx') << 16) | access_get('ax')
        ax, dx = divmod(dxax, access_get(src))
        access_set('ax', ax)
        access_set('dx', dx)
    else:
        print(f'err: invalid operand size on div')
        quit()
