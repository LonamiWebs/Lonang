from .instruction import paramcount


@paramcount(1)
def loop(m, params):
    """LOOP label"""
    dec(['cx'])
    jnz(params)
