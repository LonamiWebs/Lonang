from .statement import Statement
from functions import Function


def tag(c, m):
    """Tag definition. For instance:
        tag This is an example
    """
    c.add_code([
        f'\n; {m.group(1)}',
        f'nop\n'
    ])


tag_statement = Statement(
    r'tag  (.+)',
    tag
)
