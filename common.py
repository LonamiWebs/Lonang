
# Utilities
class strlist(list):
    def add(self, values):
        """Extends or appends the string value(s)"""
        if values is None:
            return

        if isinstance(values, str):
            self.append(values)
        elif isinstance(values, list):
            self.extend(values)
        else:
            self.append(str(values))


# Global IDs
globalid = 0
def get_uid(default=None):
    global globalid

    if default:
        return default

    result = f'_uid_{globalid}'
    globalid += 1
    return result


# Variables, and constant regexes replaced in compile time
variables = []
constants = []

# Declared functions available to use
functions = []
class Function():
    def __init__(self, m):
        # Name of the function
        self.name = m.group(1)

        # Parameter names used
        self.params = self.get_params(m.group(2))

        # Where the value is returned
        self.returns = m.group(3)

        # Used to store the code of the function
        self.code = strlist()

    @staticmethod
    def get_params(string):
        """Converts a comma separated items string into a list of items"""
        string = string.strip()
        if string:
            return [p.strip() for p in string.split(',')]
        else:
            return []

    def add(self, values):
        self.code.add(values)


class FunctionEnd():
    """Dummy special value when popping a closed brace"""


# Used when compiling, we need to know whether we push
# the code to the compiled code or to a function
defining_function = None

# Compare To Opposite jump Instruction
ctoi = {
    '<': 'jge',
    '>': 'jle',
    '<=': 'jg',
    '>=': 'jl',
    '!=': 'je',
    '==': 'jne'
}


def helperassign(dst, src):
    """Helper assign with support for assigning 8 bits to 16"""
    # TODO Add support for actually assigning CL/CH to CX (i.e. XOR the rest)
    return f'mov {dst}, {src}'


def parseint(value):
    """Tries parsing an integer value, returns None on failure"""
    try:
        if value.startswith('0x'):
            return int(value[2:], base=16)

        if value.endswith('h'):
            return int(value[:-1], base=16)

        if value.startswith('0b'):
            return int(value[2:], base=2)

        if value.endswith('b'):
            return int(value[:-1], base=2)

        return int(value)
    except ValueError:
        return None
