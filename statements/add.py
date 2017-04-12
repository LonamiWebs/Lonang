from .statement import Statement


def add(c, m):
    """Addition statement. For instance:
        dx += cx
    """
    c.add_code(f'add {m.group(1)}, {m.group(2)}')


add_statement = Statement(
    r'(\w+) \+= (VALUE)',
    add
)
