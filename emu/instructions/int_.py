from .instruction import paramcount
from parser import parseint
from datetime import datetime


def int_21h(m):
    ah = m['ah']
    if ah == 0x01:
        # Read character with output
        m['al'] = ord(m.screen.getch(echo=True))
        return True

    if ah == 0x08:
        # Read character without output
        m['al'] = ord(m.screen.getch(echo=False))
        return True

    if ah == 0x09:
        # Write string
        i = m['dx']
        while chr(m.memory[i]) != '$':
            m.screen.write(m.memory[i])
            i += 1
        m.screen.render()
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
        m.screen.write(m['al'])
        m.screen.render()
        return True
    if ah == 0x02:
        # Move cursor
        m.screen.setcur(m['dh'], m['dl'])
        return True
    if ah == 0x06:
        # Clear terminal
        m.screen.clear()
        m.screen.render()
        return True
    if ah == 0x09:
        # Print character with attribute
        # TODO BH (pager number) is ignored
        al = m['al']  # character
        bl = m['bl']  # attribute
        cx = m['cx']  # number of times

        al = chr(al) * cx
        m.screen.write(al, color=bl)
        m.screen.render()
        return True

    return False


def int_1ah(m):
    ah = m['ah']
    if ah == 0x00:
        # Ticks since midnight, around 18.20648 clock ticks per second
        now = datetime.now()
        oclock = datetime(now.year, now.month, now.day)
        ticks = int((now - oclock).total_seconds() * 18.20648)
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
