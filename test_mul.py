#!/usr/bin/python3.6

from compiler import Compiler


source = \
r'''
al = 2
al *= 3
put digit al

ah = 2
ah *= 3
put digit ah

ah = 2
al = 3
ah *= al
put digit ah

ah = 2
al = 3
al *= ah
put digit al

ax = 2
ax *= 3
put digit ax

ax = 2
dx = 3
ax *= dx
put digit ax

ax = 2
dx *= ax
put digit dx

printf "\r\n"

al = 3
al *= 260
printf "%d\r\n", al

ax = 1
ax *= 0
printf "%d\r\n", ax

ax = 1
ax *= 1
printf "%d\r\n", ax

ax = 1
ax *= -1
printf "%d\r\n", ax

ax = 1
ax *= 2
printf "%d\r\n", ax

ax = 1
ax *= -2
printf "%d\r\n", ax

ax = 1
ax *= 4
printf "%d\r\n", ax

ax = 1
ax *= -4
printf "%d\r\n", ax

ax = 1
ax *= 8
printf "%d\r\n", ax

ax = 1
ax *= -8
printf "%d\r\n", ax

ax = 1
ax *= 16
printf "%d\r\n", ax

ax = 1
ax *= -16
printf "%d\r\n", ax

ax = 1
ax *= 32
printf "%d\r\n", ax

ax = 1
ax *= -32
printf "%d\r\n", ax

ax = 1
ax *= 64
printf "%d\r\n", ax

ax = 1
ax *= -64
printf "%d\r\n", ax

ax = 1
ax *= 128
printf "%d\r\n", ax

ax = 1
ax *= -128
printf "%d\r\n", ax


; Collatz conjecture starting at 7
ax = 7
forever {
    printf "%d -> ", ax
    if ax is even {
        ax, dx = divmod ax, 2
    } else {
        ax *= 3
        ax += 1
    }
    if ax == 1 {
        break 2
    }
}
put digit 1
'''


if __name__ == '__main__':
    compiler = Compiler()
    with open('result.asm', 'w') as f:
        compiler.update_state(source)
        compiler.write(f)
