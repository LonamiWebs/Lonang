import re
from utils import stripcomments
from statements import statements
from compiler_state import CompilerState


class Compiler:
    """Lonang 8086 compiler"""
    def __init__(self):
        self.state = CompilerState()

    def update_state(self, source):
        """Updates the compiler state with the given source"""
        # TODO No corrupt state will be told although it can happen
        in_comment = False
        if isinstance(source, str):
            source = source.split('\n')

        for i, line in enumerate(source):
            # Multiline comments
            if line == ';':
                # Toggle
                in_comment = not in_comment
            if in_comment:
                # Ignore this line
                continue

            # Strip inline comments, if any
            line = stripcomments(line)
            if not line:
                continue

            if any(s.update_if_match(line, self.state) for s in statements):
                # One statement successfully matched the line and updated
                # the compiler state, so continue to the next iteration.
                # Since any() will stop on the first match, it's safe to use
                continue

            # Special case for the closing brace
            if '}' in line:
                if not self.state.close_block():
                    print(f'ERROR: Non-matching closing brace at line {i+1}')
                    return
            else:
                # Unknown line, error and early exit
                print(f'ERROR: Unknown statement at line {i+1}:\n    {line}')
                return

    def write(self, f):
        """Writes the current state to the given 'output' stream"""
        f.write('data segment\n')
        variables = sorted(
            self.state.variables.values(), key=lambda var: var.offset)

        for v in variables:
            f.write('    ')
            f.write(v.to_code())
            f.write('\n')
        f.write('ends\n')


        f.write('stack segment\n')
        f.write('    dw   128 dup(0)\n')
        f.write('ends\n')


        f.write('code segment\n')
        # Define the functions
        for function in self.state.functions.values():
            f.write(f'  {function.name} PROC\n')
            for c in function.code:
                if c[-1] != ':':
                    f.write('    ')

                # Replace constants and write
                f.write(self.state.apply_constants(c))
                f.write('\n')

            # All code for the function has been written, return
            f.write(f'    ret\n')
            f.write(f'  {function.name} ENDP\n\n')

        # Write the entry point for the program
        f.write('start:\n')

        # Set up the data segment if variables are used1
        if self.state.variables:
            f.write('    mov ax, data\n')
            f.write('    mov ds, ax\n')

        # Now write the real code part
        for c in self.state.code:
            if c[-1] != ':':
                f.write('    ')

            # Replace constants and write
            f.write(self.state.apply_constants(c))
            f.write('\n')

        f.write('\n')
        f.write('    mov ax, 4c00h\n')
        f.write('    int 21h\n')
        f.write('ends\n')

        f.write('end start\n')
