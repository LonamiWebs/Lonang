from .statement import Statement


def cls(c, m):
    """Clears the screen. For instance:
        cls
    """
    # TODO Possibly add support for not inlining
    c.add_code([
        'push ax',
        'mov ah, 6',
        'int 10h',
        'pop ax'
    ])

cls_statement = Statement(
    r'cls',
    cls
)
