import os
from importlib import import_module

ignore = [
    '__init__.py',
    'instruction.py'
]

instructions = {}

# Iterate over all the files under 'instructions' and dynamically load
# the 'filename' function calls in them to find all the statements
for filename in os.listdir('instructions'):
    fullname = os.path.join('instructions', filename)
    if os.path.isdir(fullname) or filename in ignore:
        continue

    name = os.path.splitext(filename)[0]
    module_name = 'instructions.' + name

    # Import the module 'module_name' and get the instruction method
    ins = getattr(import_module(module_name), name)
    instructions[name.strip('_')] = ins


def get_ins_params(line):
    """Extracts the instruction and the list
       of parameters passed to it on 'line'
    """
    line = line.split()
    if len(line) == 1:
        return line[0], []
    else:
        # TODO Won't work with ',' (comma character inmediate)
        params = ' '.join(line[1:]).split(',')
        return line[0], [p.strip() for p in params]
