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

string person = "Lonami"
string place = "here"

byte[] vector1 = 'A', 'B', 'C'
byte[] vector2 =  1 ,  2,   3

const VALUE = 'L' ; L value!

function myMethod(ax, bx) returns number {
    repeat bx with cx {
        number += ax
    }
}

function gcd(ax, bx) returns ax {
    if bx != 0 {
        ax, dx = divmod ax, bx
        ax = gcd(bx, dx)
    }
}

ax = 6
bx = 4
ax, bx = bx, ax

vector1[2], vector1[1], vector1[0] = vector2[0], vector2[1], vector2[2]

ax += bx

tag Starting conditionals

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

tag Method calls

dx = myMethod(7, 3)

ax = gcd(35, 15)
printf "gcd(35, 15) = %d\r\n", ax

ax = gcd(211, 173)

ax = 10
bx = 3
ax, cx = divmod ax, bx
dx += 3

forever {
    ax += 2
    dx -= 1
    if dx == 0 {
        break 2
    }
}

printf "%s, hello %s! How come you've came to %s\r\n", place, person, place

setcursor 12, little
printf "ax=%d, bx=%d, cx=%d, dx=%d", ax, bx, cx, dx
put char ' '
put digit bx
'''


if __name__ == '__main__':
    compiler = Compiler()
    with open('result.asm', 'w') as f:
        compiler.update_state(source)
        compiler.write(f)
