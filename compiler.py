import re
from functions import FunctionEnd


# TODO Should probably be called "CompilerState"
class Compiler:
    def __init__(self):
        self.uid = 0

        # Declared variables, constants and function headers
        self.variables = []
        self.constants = []
        self.functions = []

        # Parsed code
        self.code = []

        # Pending code will be added once a closing brace is found
        self.pending_code = []
        
        # Determines the function currently being defined
        self.defining_function = None

    def get_uid(self, default=None):
        """Returns a unique identifier unless
            a 'default' name is given
        """
        if default:
            return default
        
        result = f'_uid_{self.uid}'
        self.uid += 1
        return result

    def add_code(self, *values):
        """Extends the code with the given values"""
        if self.defining_function is None:
            self.code.extend(values)
        else:
            self.defining_function.add_code(*values)

    def add_pending_code(self, values):
        """Appends the given value(s) to the pending code,
            added when a closing brace is found"""
        # Append, don't extend, since we might pop many at once
        self.pending_code.append(values)

    def add_variable(self, code):
        """Appends the given code for declaring a variable"""
        self.variables.append(code)

    def add_constant(self, name, replacement):
        """Adds a new constant with the given name and the specified value"""
        regex = re.compile(fr'\b{name}\b')
        self.constants.append((regex, replacement))
    
    def apply_constants(self, code):
        """Applies the available constants to the given line of code"""
        for constant, value in self.constants:
            code = constant.sub(value, code)
        
        return code
    
    def begin_function(self, function):
        """Begins a function definition. Subsequent 'add_code' calls
            will add the code to the function body and not the main code
        """
        self.functions.append(function)
        self.defining_function = function
        
        # Used when popping pending code to determine when it ends
        self.add_pending_code(FunctionEnd)

    def close_block(self):
        """Closes a block of code, consuming one of
            the pending code saved instructions"""

        popped = self.pending_code.pop()
        if popped == FunctionEnd:
            # Defining the function ended, so clear its state
            self.defining_function = None
        else:
            if isinstance(popped, str):
                self.add_code(popped)
            else:
                self.add_code(*popped)


