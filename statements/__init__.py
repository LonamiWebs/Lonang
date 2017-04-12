# TODO Automatically load all
from .assign import assign_statement
from .add import add_statement
from .if_ import if_statement
from .else_ import else_statement
from .repeat import repeat_statement
from .variable import variable_statement
from .functiondef import functiondef_statement
from .functioncall import functioncall_statement

ignore = [
    '__init__.py',
    'utils.py',
    'statement.py'
]

statements = [
    assign_statement,
    add_statement,
    if_statement,
    else_statement,
    repeat_statement,
    variable_statement,
    functiondef_statement,
    functioncall_statement
]
