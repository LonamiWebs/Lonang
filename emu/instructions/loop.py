from .instruction import paramcount
from .dec import dec
from .jnz import jnz


@paramcount(1)
def loop(m, params):
    """LOOP label"""
    dec(m, ['cx'])
    jnz(m, params)
