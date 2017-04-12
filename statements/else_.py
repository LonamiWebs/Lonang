from .statement import Statement


def else_(c, m):
    """Else control flow statement. For instance:
        } else {
            ; code
        }
    """
    # We consume the if closing brace
    try:
        iflabel = c.pending_code.pop()
        # Ensure that it's both a string and a label
        if not isinstance(iflabel, str):
            raise ValueError('Else should be preceded by a closing "if" label, '
                             'but another pending type was found')

        if not iflabel.endswith(':'):
            raise ValueError('Else should be preceded by a closing "if" label, '
                             'but the pending code was not a label')

        # Valid label, strip the ':'
        iflabel = iflabel.strip(':')

    except IndexError:
        raise ValueError('Cannot write "else" without a previous code block '
                         '(possibly missing the previous "if"?)')
        iflabel = c.pending_code.pop()[:-1]

    # Build the else label based on the if, unless a name was provided
    if m.group(1):
        elselabel = m.group(1)
    else:
        elselabel = iflabel + '_else'

    c.add_code(
        # After the if finished, it needs to skip the else end part
        f'jmp {elselabel}',

        # Add the if label back, if this condition was not met
        # on the if jump, then we need to jump here, to the else (if label)
        f'{iflabel}:'
    )

    # After the else brace closes, ending the met if should skip the else
    c.add_pending_code(f'{elselabel}:')


else_statement = Statement(
    r'} else {',
    else_
)
