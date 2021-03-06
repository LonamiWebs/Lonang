import re
from functions import Function, FunctionEnd
from operands import Operand


class CompilerState:
    """Represents the state of the compiler, containing
        the defined variables, constants, functions and
        code, as well as handling where the code should
        be appended, either defining function or normal
        and helper functions for popping closing braces
    """

    def __init__(self):
        self.uid = 0

        # Declared variables, constants and function headers
        # They are dictionaries so two cannot be declared with the same name
        self.variables = {}
        self.constants = {}
        self.functions = {}

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

    def add_code(self, values):
        """Extends the code with the given values"""
        if self.defining_function is None:
            if isinstance(values, str):
                self.code.append(values)
            else:
                self.code.extend(values)
        else:
            self.defining_function.add_code(values)

    def add_pending_code(self, values):
        """Appends the given value(s) to the pending code,
            added when a closing brace is found"""
        # Append, don't extend, since we might pop many at once
        self.pending_code.append(values)

    def add_variable(self, variable):
        """Appends the given Variable, redefining it if required"""
        if variable.is_constant:
            self.add_constant(variable.name, variable.value)
        else:
            variable.offset = sum(v.length * (v.size // 8)
                                  for v in self.variables.values())

            self.variables[variable.name] = variable

    def add_constant(self, name, replacement):
        """Adds a new constant with the given name and the specified value"""
        regex = re.compile(fr'\b{name}\b')
        self.constants[name] = (regex, replacement)

    def apply_constants(self, code):
        """Applies the available constants to the given line of code"""
        code = str(code)
        for constant, value in self.constants.values():
            code = constant.sub(value, code)

        return code

    def get_operands(self, csv):
        """Converts the possibly comma separated values to a
            list of operands (inmediate, registers and variables
        """
        if isinstance(csv, list):
            return [v if isinstance(v, Operand)
                      else Operand(self, v)
                      for v in csv]

        if isinstance(csv, Operand):
            return [csv]

        return [Operand(self, v) for v in Operand.get_csv(csv)]

    def find_matching_function(self, name, param_count, must_return):
        """Finds and returns the function definition which
            matches with the given 'name' and parameter count.

            If 'must_return' is True, then the function must also
            return some value to be valid
        """
        f = self.functions.get(Function.mangle(name, param_count))
        if f and (not must_return or f.returns is not None):
            return f

        return None

    def begin_function(self, function):
        """Begins a function definition. Subsequent 'add_code' calls
            will add the code to the function body and not the main code
        """
        self.functions[function.name] = function
        self.defining_function = function

        # Used when popping pending code to determine when it ends
        self.add_pending_code(FunctionEnd)

    def close_block(self):
        """Closes a block of code, consuming one of
            the pending code saved instructions.

            Returns True if the block was successfully closed"""
        try:
            popped = self.pending_code.pop()
        except IndexError:
            return False

        if popped == FunctionEnd:
            # Defining the function ended, so clear its state
            self.defining_function = None
        else:
            self.add_code(popped)

        return True
