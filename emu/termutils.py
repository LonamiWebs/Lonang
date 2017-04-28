import sys


def putch(ch):
    """Puts a character on the console"""
    if isinstance(ch, int):
        ch = chr(ch)

    if ch == '\r':
        return
    if ch == '\n':
        print()
    else:
        print(ch, end='')
        sys.stdout.flush()


def get_colorama_color(bg_fg):
    """Gets the terminal sequence for colorama to color the terminal
       given the a 8 bits color (high 4 for background, low for foreground)
    """
    bg = bg_fg >> 4
    fg = bg_fg & 0xf
    translation = {
        # rgb
        0b000: 0,  # black
        0b001: 4,  # blue
        0b010: 2,  # green
        0b011: 6,  # cyan
        0b100: 1,  # red
        0b101: 5,  # magent
        0b110: 3,  # yellow
        0b111: 7,  # white
    }
    bg_light = (bg & 8) != 0
    fg_light = (fg & 8) != 0
    bg = 40 + translation[bg & 7]
    fg = 30 + translation[fg & 7]
    
    if bg_light:
        bg += 60
    if fg_light:
        fg += 60
    
    return f'\033[{bg}m\033[{fg}m'


# http://stackoverflow.com/a/510364
try:
    import msvcrt
    def getch(echo):
        """Gets a character from the console"""
        sys.stdout.flush()
        ch = msvcrt.getch()
        if echo:
            print(ch, end='')
        return msvcrt.getch()

except ImportError:
    import sys, tty, termios
    def getch(echo):
        """Gets a character from the console"""
        sys.stdout.flush()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if echo:
            print(ch, end='')
        return ch

    def __call__(self):
        return self.impl()
