from .instruction import paramcount


@paramcount(2)
def shl(m, params):
    """SHL dst, src"""
    # TODO Set flags, and only cx or inmediate should be valid
    dst, src = params
    access_set(dst, access_get(dst) << access_get(src))
