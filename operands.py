import re


class Operand:
    """Anything that can be used as an operand
       such as a number, character, register or
       a variable stored in memory
    """
    def __init__(self, c, name, assert_vector_access=True):
        self.name = c.apply_constants(name).strip()

        # Check if we're accessing to a vectors length
        m = re.search(r'\s*\.\s*length$', self.name)
        is_inmediate_length = m is not None

        if is_inmediate_length:
            # We're accessing the length of a variable, ensure it's a vector
            self.name = self.name[:m.start()]
            var = self._get_variable_or_raise(c, self.name)
            if not var.is_vector:
                raise ValueError(f'Cannot access the length of the non-vector '
                                 f'variable "{self.name}"')

            self.value = var.length
        else:
            # Not accessing the length of a variable, might be an inmediate
            # print('nay', self.name)
            self.value = self.parseint(self.name)

        # Default values
        self.index = None
        self.is_reg = False
        self.is_mem = False

        if self.value is not None:
            self.code = str(self.value)
            self.size = self.value.bit_length()
            if self.value < 0:
                self.size += 1  # Bit sign

        elif self.is_register(self.name):
            self.is_reg = True
            self.name = self.name.lower()
            self.code = self.name
            self.size = 8 if self.name[-1] in 'hl' else 16
            # Access to the low/high part if supported
            if self.name[-1] in 'xhl':
                self.full = self.name[0] + 'x'
                self.high = self.name[0] + 'h'
                self.low = self.name[0] + 'l'
            else:
                self.full = self.name
                self.high = self.low = None

        else:
            self.is_mem = True
            if '[' in self.name:
                self.name, self.index = self.name.split('[')
                self.index = self.index.split(']')[0].strip()
                # TODO Assert index is OK

            var = self._get_variable_or_raise(c, self.name)
            if assert_vector_access and var.is_vector and self.index is None:
                raise ValueError(f'Vector variables must be indexed on access')

            self.size = var.size
            self.type = var.type
            self.is_vector = var.is_vector
            if self.index is None:
                self.code = self.name
            else:
                self.code = f'{self.name}[{self.index}]'

    @staticmethod
    def _get_variable_or_raise(c, name):
        """Gets the variable with the specified name, or raises"""
        var = c.variables.get(name, None)
        if var is None:
            raise ValueError(f'No variable called "{name}" found')
        return var

    @staticmethod
    def is_register(name):
        """Returns True if the given 'name' is a register"""
        if len(name) != 2:
            return False

        name = name.lower()
        if name[0] in 'abcd' and name[1] in 'xhl':
            return True

        return name in ('si', 'di', 'cs', 'ds', 'ss', 'sp', 'bp', 'es')

    @staticmethod
    def parseint(value):
        """Tries parsing an integer value, returns None on failure"""
        if not value or not value.strip():
            return None

        value = value.strip()
        try:
            if value[0] == "'" and value[-1] == "'":
                value = value.strip("'").encode('ascii').decode('unicode_escape')
                if len(value) != 1:
                    raise ValueError('A character value can only be 1 character')

                return ord(value[0])

            value = value.lower()
            if value.startswith('0x'):
                return int(value[2:], base=16)

            if value[0].isdigit() and value[-1] == 'h':
                return int(value[:-1], base=16)

            if value.startswith('0b'):
                return int(value[2:], base=2)

            if value[0].isdigit() and value[-1] == 'b':
                return int(value[:-1], base=2)

            return int(value)
        except ValueError:
            return None

    @staticmethod
    def get_csv(values):
        """If 'values' is not a list already, converts the
            comma separated values to a list of STRING values
        """
        if not values:
            return []

        if isinstance(values, list):
            return values

        if values.strip():
            return [v.strip() for v in values.split(',')]
        else:
            return []

    def __eq__(self, b):
        return self.code == b.code

    def __str__(self):
        return self.code

    def __hash__(self):
        return hash(self.code)

    def __getitem__(self, key):
        return self.code[key]
