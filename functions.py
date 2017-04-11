class Function:
    def __init__(self, m):
        # Name of the function
        self.name = m.group(1)

        # Parameter names used
        self.params = self.get_params(m.group(2))

        # Where the value is returned
        self.returns = m.group(3)

        # Used to store the code of the function
        self.code = []

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
        self.code.extend(values)


class FunctionEnd():
    """Dummy special value when popping a closed brace"""
