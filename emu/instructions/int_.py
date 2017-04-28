from .instruction import paramcount
from parser import parseint
from termutils import putch, getch, get_colorama_color


try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None


def int_21h(m):
    ah = m['ah']
    if ah == 0x01:
        # Read character with output
        m['al'] = ord(getch(echo=True))
        return True

    if ah == 0x08:
        # Read character without output
        m['al'] = ord(getch(echo=False))
        return True

    if ah == 0x09:
        # Write string
        i = m['dx']
        while chr(m.memory[i]) != '$':
            putch(m.memory[i])
            i += 1
        return True

    if ah == 0x4c:
        # Machine halt
        print('success: machine halted')
        quit()
        return True

    return False


def int_10h(m):
    ah = m['ah']
    if ah == 0x0e:
        # Teletype output
        putch(m['al'])
        return True
    if ah == 0x02:
        # Move cursor
        if colorama is None:
            print('err: pip colorama is required for INT 10h / AH = 02h')
            quit()

        pos = lambda y, x: '\x1b[%d;%dH' % (y, x)
        row, col = m['dh'], m['dl']
        print(pos(row, col))
        return True
    if ah == 0x06:
        # Clear terminal
        clear()
        return True
    if ah == 0x09:
        # Print character with attribute
        # TODO BH (pager number) is ignored
        if colorama is None:
            print('err: pip colorama is required for INT 10h / AH = 09h')
            quit()

        al = m['al']  # character
        bl = m['bl']  # attribute
        cx = m['cx']  # number of times
        print(get_colorama_color(bl))
        for _ in range(cx):
            putch(al)
        print(colorama.Style.RESET_ALL)
        return True

    return False


def int_1ah(m):
    ah = m['ah']
    if ah == 0x00:
        # Ticks since midnight, around 18.20648 clock ticks per second
        now = datetime.now()
        oclock = datetime(now.year, now.month, now.day)
        ticks = (now - oclock).seconds
        m['dx'] = ticks & 0xffff
        ticks >>= 16
        m['cx'] = ticks & 0xffff
        m['al'] = 0
        return True

    return False


@paramcount(1)
def int_(m, params):
    """INT code"""
    code = parseint(params[0])
    if code == 0x21 and int_21h(m):
        return
    if code == 0x10 and int_10h(m):
        return
    if code == 0x1a and int_1ah(m):
        return

    print(f'err: interrupt {hex(code)} not implemented')
    quit()
