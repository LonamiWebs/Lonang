class Variable:
    def __init__(self, name, vartype, value):
        self.name = name
        self.type = vartype
        self.value = value.strip()

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
        return f'{self.name} {self.typecode} {self.value}'

    def __str__(self):
        return self.to_code()
