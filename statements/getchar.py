from .statement import Statement
from utils import helperassign
from variables import TmpVariables


def getchar(c, m):
    """Gets a character from the keyboard. For instance:
        al = get char
        cx = get digit

        Note that 'get digit' will not perform bound checking.
        The caller is responsible to check that the read digit
        is greater or equal than zero and less than ten
    """
    # TODO Possibly add support for not inlining
    dst = m.group(1)
    digit = m.group(2) == 'digit'
    # Defaults to 'show' (if it's None, or it's not 'hide')
    show = m.group(3) != 'hide'

    # If dst = 'ah', we've used 'al'
    # If dst = 'al', we've used 'ah'
    # If dst = anything, we've used both
    tmps = TmpVariables(c)

    if dst[0] == 'a':
        if dst[-1] == 'h':
            tmps.save('al')
        elif dst[-1] == 'l':
            tmps.save('ah')
        else:
            tmps.save('ax')
    else:
        tmps.save('ax')

    # 1 to echo the keystroke, 7 not to
    c.add_code([
        'mov ah, 1' if show else 'mov ah, 7',
        'int 21h'
    ])

    if digit:
        c.add_code("sub al, '0'")

    helperassign(c, dst, 'al')
    tmps.restore_all()


getchar_statement = Statement(
    r'(VAR) = get  (char|digit)(?:  (show|hide))?',
    getchar
)
