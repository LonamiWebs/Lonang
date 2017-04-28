from .statement import Statement
from utils import ctoi
import re


label_re = re.compile('^(\w+):$')


def break_(c, m):
    """Break control flow statement. For instance:
        while ax == ax {
            if ax > 8 {
                break 2
            }
            ax += 1
        }
        ; breaks two levels exiting here 
    """
    global label_re

    original_count = 1 if m.group(1) is None else int(m.group(1))
    count = original_count
    for line in reversed(c.pending_code):
        if isinstance(line, str):
            label = label_re.match(line)
            if label:
                count -= 1
        else:
            for l in line:
                label = label_re.match(l)
                if label:
                    count -= 1
                    break

        if count == 0:
            c.add_code(f'jmp {label.group(1)}')
            break

    if count > 0:
        raise ValueError(f'Could not break from {original_count} block(s)')


break_statement = Statement(
    r'break(  \d+)?',
    break_
)
