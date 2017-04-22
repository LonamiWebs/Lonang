import re
from utils import get_csv


class Function:
    def __init__(self, name, params, returns=None, mangle=True):
        # Convert a comma separated list to normal parameters if required
        self.params = get_csv(params)

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

    def add_code(self, values):
        """Extends or appends the string value(s) for the code"""
        if isinstance(values, str):
            self.code.append(values)
        else:
            self.code.extend(values)


class FunctionEnd():
    """Dummy special value when popping a closed brace"""
