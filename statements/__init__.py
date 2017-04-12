import os
from importlib import import_module

ignore = [
    '__init__.py',
    'utils.py',
    'statement.py'
]

statements = []

# Iterate over all the files under 'statements' and dynamically load
# the 'filename_statement' variables in them to find all the statements
for filename in os.listdir('statements'):
    if os.path.isdir(filename) or filename in ignore:
        continue

    name = os.path.splitext(filename)[0]
    module_name = 'statements.' + name
    statement_name = name.strip('_') + '_statement'

    # Import the module 'module_name' and get the statement variable
    statement = getattr(import_module(module_name), statement_name)
    statements.append(statement)

