#!/usr/bin/python3.6

from compiler import Compiler


source = \
r'''
short number = 0
byte lnumber = 0
ax = 0x901

; Registers ;

dx = ax
printf("dx should be 2305 and is %d\r\n", dx)
dx = ah
printf("dx should be 9 and is %d\r\n", dx)
dx = al
printf("dx should be 1 and is %d\r\n", dx)
dh = ax
printf("dh should be 1 and is %d\r\n", dh)  ; FAIL!!!

; Register to memory ;
number = ax
printf("number should be 2305 and is %d\r\n", number)
number = ah
printf("number should be 9 and is %d\r\n", number)
number = al
printf("number should be 1 and is %d\r\n", number)

lnumber = ax
printf("lnumber should be 1 and is %d\r\n", lnumber)  ; FAIL!!!
lnumber = ah
printf("lnumber should be 9 and is %d\r\n", lnumber)  ; FAIL!!!
lnumber = al
printf("lnumber should be 1 and is %d\r\n", lnumber)  ; FAIL!!!

; Memory to register ;
number = 0x901
lnumber = 5

ax = number
printf("ax should be 2305 and is %d\r\n", ax)
ah = number
printf("ah should be 1 and is %d\r\n", ah)  ; FAIL!!!
al = number
printf("al should be 1 and is %d\r\n", al)  ; FAIL!!!

ax = lnumber
printf("ax should be 5 and is %d\r\n", ax)
ah = lnumber
printf("ah should be 5 and is %d\r\n", ah)  ; FAIL!!!
al = lnumber
printf("al should be 5 and is %d\r\n", al)  ; FAIL!!!

; TODO Test with registers not high/low part such as 'si' or 'di'

'''


if __name__ == '__main__':
    compiler = Compiler()
    with open('result.asm', 'w') as f:
        compiler.update_state(source)
        compiler.write(f)
