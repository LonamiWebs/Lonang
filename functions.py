import re


class Function:
    def __init__(self, name, params, returns=None, mangle=True):
        # Convert a comma separated list to normal parameters if required
        self.params = params if isinstance(params, list)\
                             else self.get_params(params)

        # Name mangling, add as many underscores as parameter count
        if mangle:
            self.name = self.mangle(name, len(self.params))
        else:
            self.name = name

        # Where the value is returned
        self.returns = returns

        # Used to store the code of the function
        self.code = []

    @staticmethod
    def mangle(name, param_count):
        return name + '_' * param_count

    @staticmethod
    def get_params(string):
        """Converts a comma separated items string into a list of items"""
        string = string.strip()
        if string:
            return [p.strip() for p in string.split(',')]
        else:
            return []

    def add_code(self, *values):
        """Extends or appends the string value(s) for the code"""
        self.code.extend(v for v in values if v is not None)


class FunctionEnd():
    """Dummy special value when popping a closed brace"""


# Underscore not supported must start with a letter
# TODO This could probably be used on variable names too
FUNC_NAME_RE = r'[A-Za-z][A-Za-z0-9]*'
