from .instruction import paramcount


def int_21h(params):
    if ah == 0x01:
        # Read character with output
        access_set('al', ord(getch(echo=True)))
        return

    if ah == 0x08:
        # Read character without output
        print()
        access_set('al', ord(getch(echo=False)))
        return

    if ah == 0x09:
        # Write string
        i = access_get('dx')
        while chr(memory[i]) != '$':
            putch(memory[i])
            i += 1
        return

    if ah == 0x4c:
        # Machine halt
        print('success: machine halted')
        quit()
        return


def int_10h(params):
    if ah == 0x0e:
        # Teletype output
        al = access_get('al')
        putch(al)
        return
    if ah == 0x02:
        # Move cursor
        if colorama is None:
            print('err: pip colorama is required for INT 10h / AH = 02h')
            quit()

        pos = lambda y, x: '\x1b[%d;%dH' % (y, x)
        row, col = access_get('dh'), access_get('dl')
        print(pos(row, col))
        return
    if ah == 0x06:
        # Clear terminal
        clear()
        return
    if ah == 0x09:
        # Print character with attribute
        # TODO BH (pager number) is ignored
        if colorama is None:
            print('err: pip colorama is required for INT 10h / AH = 09h')
            quit()

        al = access_get('al')  # character
        bl = access_get('bl')  # attribute
        cx = access_get('cx')  # number of times
        print(get_colorama_color(bl))
        for _ in range(cx):
            putch(al)
        print(colorama.Style.RESET_ALL)
        return


def int_1ah(params):
    if ah == 0x00:
        # Ticks since midnight, around 18.20648 clock ticks per second
        now = datetime.now()
        oclock = datetime(now.year, now.month, now.day)
        ticks = (now - oclock).seconds
        access_set('dx', ticks & 0xffff)
        ticks >>= 16
        access_set('cx', ticks & 0xffff)
        access_set('al', 0)
        return


@paramcount(1)
def int_(m, params):
    """INT code"""
    code = parseint(params[0])
    ah = access_get('ah')
    if code == 0x21:
        int_21h(params)
    if code == 0x10:
        int_10h(params)
    if code == 0x1a:
        int_1ah(params)

    print(f'err: interrupt {hex(code)} not implemented')
    print(registers['ip'])
    print('\n'.join(lines[registers['ip']-2:registers['ip']+2]))
    quit()
