#!/usr/bin/python3.6

import re
from statements import *
from compiler import Compiler

source = \
r'''

;
; This is a comment.
; Accross many lines
;

short number = 4242
byte little = 24
string mystr = "Hello\r\nworld!"
const VALUE = 'L' ; L value!

function myMethod(ax, bx) returns number {
    repeat bx with cx {
        number += ax
    }
}

ax = 4
bx = 6
ax += bx

if bx == 6 { @primerIf
    ax = VALUE
}

bx = 0
repeat 2 with cx { @primerLoop
    if ax < 10 {
        bx += 1
    }

    ax += 1
}

dx = myMethod(7, 3)

'''


def parse(compiler, source):
    """Parses the given 'source' and stores the state on 'compiler'"""
    in_comment = False
    for i, line in enumerate(source.split('\n')):
        # Multiline comments
        if line == ';':
            # Toggle
            in_comment = not in_comment
        if in_comment:
            # Ignore this line
            continue

        # Delete everything after the semicolon (inline comment)
        if ';' in line:
            line = line[:line.index(';')]

        line = line.strip()
        if not line:
            continue

        ok = False
        for regex, geti in regex_getis:
            m = regex.match(line)
            if m:
                ok = True
                # TODO Rename "geti" since it doesn't anymore
                #      get any instruction but rather uses the
                #      compiler to add the code to it
                geti(compiler, m)
                break

        if ok:
            continue

        # Special case for the closing brace
        if '}' in line:
            # TODO Try except here, return None?
            #      f'ERROR: Non-matching closing brace at line {i+1}'
            compiler.close_block()
        else:
            # Unknown line, error and early exit
            print(f'ERROR: Unknown statement at line {i+1}:\n    {line}')
            return

    # Done!
    pass


# TODO Yes, it's more like CompilerState
compiler = Compiler()
parse(compiler, source)


# TODO Compiler should have something to tell its OK state
# if ok:
with open('result.asm', 'w') as f:
    f.write('data segment\n')
    for v in compiler.variables:
        f.write('    ')
        f.write(v)
        f.write('\n')
    f.write('ends\n')


    f.write('stack segment\n')
    f.write('    dw   128 dup(0)\n')
    f.write('ends\n')


    f.write('code segment\n')
    # Define the functions
    for function in compiler.functions:
        f.write(f'  {function.name} PROC\n')
        for c in function.code:
            if c[-1] != ':':
                f.write('    ')

            # Replace constants and write
            f.write(compiler.apply_constants(c))
            f.write('\n')

        # All code for the function has been written, return
        f.write(f'    ret\n')
        f.write(f'  {function.name} ENDP\n\n')

    # Write the entry point for the program
    f.write('start:\n')
    for c in compiler.code:
        if c[-1] != ':':
            f.write('    ')

        # Replace constants
        for constant, value in compiler.constants:
            c = constant.sub(value, c)

        f.write(c)
        f.write('\n')

    f.write('\n')
    f.write('    mov ax, 4c00h\n')
    f.write('    int 21h\n')
    f.write('ends\n')

    f.write('end start\n')

print('The following source was parsed successfully:')
print(source.strip())
