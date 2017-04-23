class Operand:
    """Anything that can be used as an operand
       such as a number, character, register or
       a variable stored in memory
    """
    def __init__(self, c, name, assert_vector_access=True):
        self.name = c.apply_constants(name).strip()
        self.value = self.get_value(self.name)

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

            var = c.variables.get(self.name, None)
            if var is None:
                raise ValueError(f'No variable called "{self.name}" found')

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
    def get_value(value):
        """Gets the integer value for 'value', or None on failure"""
        if not value or not value.strip():
            return None

        value = value.strip()
        try:
            if value[0] == "'" and value[-1] == "'":
                return ord(value[1])

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
    def is_register(name):
        """Returns True if the given 'name' is a register"""
        if len(name) != 2:
            return False

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
                return ord(value[1])

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
