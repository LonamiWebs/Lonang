from parser import parseint, parse_memory_addr
from parser import pack_value, unpack_value
from screen_buffer import ScreenBuffer


class Machine:
    """Represents an 8086 machine"""
    def __init__(self):
        # TODO We actually don't care about DS value, but we should
        self.memory = []

        # Name and location for certain indices (and type size) in memory
        #   name: (index, size)
        self.memory_nameloc = {}

        # TODO Infinite stack, not actually what was reserved
        self.stack = []

        # Machine registers (general purpose, instruction pointer, flags...)
        self.registers = {
            n: 0 for n in 'ax bx cx dx cs ip ss sp bp si di ds es'.split()
        }
        self.flags = {
            f: False for f in 'cf zf sf of pf af if df'.split()
        }

        # Machine labels used on jumps TODO Doesn't sound like a good idea
        self.labels = {}

        # Machine's screen buffer output
        self.screen = ScreenBuffer()


    def _isregister(self, name):
        """Returns True if the given 'name' is a register"""
        name = name.lower()
        if name[-1] in 'xhl':
            return f'{name[0]}x' in self.registers
        else:
            return name in self.registers or name in self.flags


    def tag_memory(self, name, size):
        """Tags the current memory size with the given name and size"""
        self.memory_nameloc[name] = len(self.memory), size


    def get_memory_addr(self, tag_name):
        """Gets the memory index for the given tag name"""
        return self.memory_nameloc[tag_name][0]


    def add_to_memory(self, values):
        """Adds the given value(s) to memory"""
        if isinstance(values, list):
            self.memory.extend(values)
        else:
            self.memory.append(value)


    def update_flags(self, result, size):
        """Updates the flags state when 'result'
           happens on 'size' operands
        """
        # Carry flag (CF)
        # Parity flag (PF)
        # Auxiliary carry flag (AF)
        # Zero flag (ZF)
        # Sign flag (SF)
        # Trap flag (TF)
        # Interrupt flag (IF)
        # Direction flag (DF)
        # Overflow flag (OF)
        # TODO flags: AF; TF; IF; DF
        # TODO size = max(access_size(op1), access_size(op2))
        self.flags['cf'] = result >= 2**size
        self.flags['zf'] = result == 0
        self.flags['sf'] = (result & (1 << (size - 1))) != 0

        r = result
        self.flags['pf'] = True
        while r > 0:
            if r & 1 == 1:
                self.flags['pf'] = not self.flags['pf']
            r >>= 1

        # A negative result out of positive operands (or vice versa) is an overflow
        power = 2**size
        if result < 0:
            comp = ((result ^ (power - 1)) + 1) & power - 1
        else:
            comp = result

        self.flags['of'] = comp < 0 or comp >= 2**(size-1)


    def push(self, value):
        """Pushes the given value to the stack"""
        self.stack.append(value)


    def pop(self):
        """Pops a value from the machine's stack"""
        return self.stack.pop()


    def __getitem__(self, name):
        """Accesses to the given name (register, memory...)"""
        if not name:
            return 0

        # TODO Maybe from "parser" import parsint, like code parser...
        #      or better parseexpr
        value = parseint(name)
        if value is not None:
            return value

        if self._isregister(name):
            name = name.lower()
            if name[-1] == 'f':
                return self.flags[name]
            elif name[-1] == 'h':
                name = f'{name[0]}x'
                return self.registers[name] >> 8
            elif name[-1] == 'l':
                name = f'{name[0]}x'
                return self.registers[name] & 0xff
            else:
                return self.registers[name]
        else:
            if name.lower() == 'data':
                # TODO Not actually returning the location of DS
                return 0

            if '[' in name:
                # TODO Seems like indirect memory access is treated as 8 bits
                idx = parse_memory_addr(self, name)
                size = 8
                take = 1
            else:
                idx, size = self.memory_nameloc[name]
                take = size // 8

            mem = self.memory[idx:idx+take]
            return unpack_value(mem, size)


    def __setitem__(self, name, value):
        """Accesses to the given name (register, memory...)"""
        # TODO Assert it doesn't access invalid sizes
        if self._isregister(name):
            if name[-1] == 'f':
                self.flags[name] = value

            if name[-1] == 'h':
                name = f'{name[0]}x'
                result = (self.registers[name] & 0x00ff) | (value << 8)
                self.registers[name] = result

            elif name[-1] == 'l':
                name = f'{name[0]}x'
                result = (self.registers[name] & 0xff00) |  value
                self.registers[name] = result

            else:
                self.registers[name] = value

        else:
            if '[' in name:
                # TODO Seems like indirect memory access is treated as 8 bits
                idx = parse_memory_addr(self, name)
                size = 8
                take = 1
            else:
                idx, size = self.memory_nameloc[name]
                take = size // 8

            self.memory[idx:idx+take] = pack_value(value, size)

    def sizeof(self, name):
        """Determines the size of the given name"""
        if not name:
            return 0

        value = parseint(name)
        if value is not None:
            if value.bit_length() <= 8:
                return 8
            if value.bit_length() <= 16:
                return 16

        if self._isregister(name):
            name = name.lower()
            if name[-1] == 'f':
                return 1
            elif name[-1] in 'hl':
                return 8
            else:
                return 16
        else:
            if '[' in name:
                name = name[:name.index('[')]
                if not name:
                    return 8

            _, size = self.memory_nameloc[name]
            return size

        print(f'err: could not determine size of {name}')
        quit()
