#!/usr/bin/python3.6

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

    while bx < 9 {
        bx += 1
    }
}

bx = 0
while bx == 1 or once {
    bx += 2
}

repeat 2 with cx { @primerLoop
    if ax < 10 {
        bx += 1
    }

    ax += 1
}

dx = myMethod(7, 3)

'''


if __name__ == '__main__':
    compiler = Compiler()
    with open('result.asm', 'w') as f:
        compiler.update_state(source)
        compiler.write(f)
