class Variable:
    def __init__(self, name, vartype, value):
        self.name = name
        self.value = value.strip()

        # If the type ends with ']' then it probably is a vector
        self.is_vector = vartype.endswith(']') and '[' in vartype
        if self.is_vector:
            vartype, self.length = vartype.split('[')
            try:
                self.length = int(self.length[:-1].strip())
            except ValueError:
                raise ValueError(f'Unknown length value "{self.length[:-1]}"')

        self.is_constant = vartype == 'const'
        if self.is_constant:
            self.typecode = None
        else:
            if vartype == 'byte':
                self.typecode = 'DB'

            elif vartype == 'short':
                self.typecode = 'DW'

            elif vartype == 'string':
                self.typecode = 'DB'
                self.value = self.escape_string(value)

            else:
                raise ValueError(f'Unknown variable type "{vartype}"')

    @staticmethod
    def escape_string(string):
        """Escapes the given string so it's valid to be assigned to a
            string variable"""
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
            # TODO Support for non-duplicate values, thus length inferred
            return f'{self.name} {self.typecode} {self.length} dup({self.value})'
        else:
            return f'{self.name} {self.typecode} {self.value}'

    def __str__(self):
        return self.to_code()
