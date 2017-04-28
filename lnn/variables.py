from operands import Operand


class Variable:
    def __init__(self, name, vartype, value, vector_size=None):
        self.name = name

        # 'vector_size' should be None for non-vector types
        self.is_vector = vector_size is not None
        if self.is_vector:
            if vector_size < 1:
                raise ValueError('Vector size must be ≥ 1')

            self.value = Operand.get_csv(value)
            self.length = vector_size
            # One value is OK with any vector size, 'dup()' is assumed
            if len(self.value) != 1 and self.length != len(self.value):
                raise ValueError(
                    f'Specified vector length ({self.length}) and supplied '
                    f'values count ({len(self.value)}) do not match')
        else:
            # Not a vector, so save its single value
            self.value = value.strip()

        # Name and vector handled, now define the type
        self.type = vartype

        # Type defined, now determine its code
        self.is_constant = vartype == 'const'
        if self.is_constant:
            if self.is_vector:
                raise ValueError('Cannot define a constant vector')

            self.typecode = None
        else:
            if vartype == 'byte':
                self.typecode = 'DB'
                self.size = 8

            elif vartype == 'short':
                self.typecode = 'DW'
                self.size = 16

            elif vartype == 'string':
                if self.is_vector:
                    raise ValueError('Cannot define a vector of strings')

                self.typecode = 'DB'
                self.size = 8
                self.value = self.escape_string(value)

            else:
                raise ValueError(f'Unknown variable type "{vartype}"')

    @staticmethod
    def escape_string(string):
        """Escapes the given string so it's valid to be assigned to a
            string variable"""
        # TODO Ensure it's a valid string, and that it's not already formatted
        analyzed = string.strip('"').encode('ascii').decode('unicode_escape')
        quote_open = False
        result = ''

        for a in analyzed:
            if ord(a) < 32:
                # Non-printable
                if quote_open:
                    result += '", '
                    quote_open = False
                result += str(ord(a))
                result += ', '
            else:
                # Printable
                if not quote_open:
                    result += '"'
                    quote_open = True
                result += a

        if quote_open:
            result += '", '

        result += "'$'"
        return result

    def to_code(self):
        """Returns the code representation for
            the definition of this variable"""
        if self.is_vector:
            if len(self.value) != self.length:
                return f'{self.name} {self.typecode} {self.length} dup({self.value[0]})'
            else:
                return f'{self.name} {self.typecode} {", ".join(self.value)}'
        else:
            return f'{self.name} {self.typecode} {self.value}'

    def __str__(self):
        return self.to_code()


class TmpVariables:
    def __init__(self, c):
        self.c = c
        self.saved = {}

    def save(self, register):
        """Defines a temporary variable for the given
            register, to be used instead of the stack.

            Returns the name of the temporary variable.
        """
        name = self.saved.get(register, None)
        if name is None:
            # First time defining it, add it to our saved dictionary
            size = 8 if register[-1] in 'hl' else 16
            name = self.create_tmp(register, size)
            self.saved[register] = name

        # No need for helperassign, we really know it's okay to move
        self.c.add_code(f'mov {name}, {register}')

    def create_tmp(self, name, size):
        """Creates a temporary variable with the given name,
            and returns the name of the temporary variable"""
        name = f'_v_tmp_{name}'
        if name not in self.c.variables:
            # First time defining it ever for this compiler state,
            # add the newly declared variable to it
            self.c.add_variable(Variable(
                name,
                'byte' if size == 8 else 'short',
                value='?'
            ))

        return name

    def restore(self, register):
        """Restores the specified register from
            its corresponding temporary variable"""
        # No need for helperassign, we really know it's okay to move
        self.c.add_code(f'mov {register}, {self[register]}')

    def save_all(self, registers):
        """Shorthand to save the list of registers"""
        for r in registers:
            self.save(r)

    def restore_all(self):
        """Shorthand to restore all registers"""
        for r in self.saved:
            self.restore(r)

    def __contains__(self, register):
        return register in self.saved

    def __getitem__(self, register):
        name = self.saved.get(register, None)
        if name is None:
            raise ValueError(f'"{register}" was not temporary saved')
        return name
