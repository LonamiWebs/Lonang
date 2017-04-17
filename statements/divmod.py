from .statement import Statement
from utils import helperassign, parseint


def divmod_(c, m):
    """Division & Modulo statement. For instance:
        ax, dx = divmod bx, 7

        After this operation takes place, the values will be:
        ax = bx / 7  ; (integer division)
        dx = bx % 7  ; (bx modulo 7)
    """
    a = parseint(m.group(3))
    b = parseint(m.group(4))
    if a is not None and b is not None:
        # Both are integers, we can optimize this away
        # and just plug the right values in
        a, b = divmod(a, b)
        helperassign(c, m.group(1), a)
        helperassign(c, m.group(2), b)
    else:
        # Need to perform the operation
        quotient = m.group(1)
        remainder = m.group(2)
        dividend = m.group(3)
        divisor = m.group(4)
        # TODO Support for AH/AL (8 bits division mode)

        # Only AX and DX will be affected, so unless we're
        # assigning a result to them, they need to be pushed
        push_ax = quotient != 'ax' and remainder != 'ax'
        push_dx = quotient != 'dx' and remainder != 'dx'
        if push_ax:
            c.add_code('push ax')
        if push_dx:
            c.add_code('push dx')

        push_divisor = False
        # Determine the divisor to be used, it cannot be 'dx' since
        # it has to be zero because it's taken into account when dividing,
        # and it cannot be 'ax' because it's where the dividend is
        #
        # The divisor cannot be an inmediate value either ('b' not None)
        if divisor in ['ax', 'dx'] or b is not None:
            # Pick either the quotient or remainder (will be overwritten later)
            if quotient not in ['ax', 'dx']:
                used_divisor = quotient
            elif remainder not in ['ax', 'dx']:
                used_divisor = remainder
            else:
                # No luck, use 'bx' for instance (we need to save it)
                used_divisor = 'bx'
                push_divisor = True
                c.add_code('push bx')

            # Update whatever register we used
            helperassign(c, used_divisor, divisor)
        else:
            # We have the right value for the divisor, no move required
            used_divisor = divisor

        # Divisor set up, neither in 'ax' nor 'dx' so it's OK
        # Now set up the dividend, which must always be in 'ax'
        helperassign(c, 'ax', dividend)

        # Everything set, perform the division
        c.add_code(f'xor dx, dx')  # Upper bits are considered!
        c.add_code(f'div {used_divisor}')

        if push_divisor:
            # Division done, restore our temporary register
            c.add_code('pop bx')

        # Now move the result if required
        # Special case, 'ax' and 'dx are swapped
        if quotient == 'dx' and remainder == 'ax':
            c.add_code('push ax',
                       'mov ax, dx',
                       'pop dx')
        else:
            # Although helperassign would take care of these, we can
            # slightly optimize away the otherwise involved push/pop
            #
            # TODO Actually, perhaps helper assign could note this and
            # swap the order of assignment
            if quotient == 'dx':
                # Special case, we need to move remainder, in 'dx', first
                helperassign(c, [remainder, quotient], ['dx', 'ax'])
            else:
                # Normal case, first 'ax', then 'dx'
                helperassign(c, [quotient, remainder], ['ax', 'dx'])

        if push_dx:
            c.add_code('pop dx')
        if push_ax:
            c.add_code('pop ax')
      

divmod_statement = Statement(
    r'(\w+) , (\w+) = divmod \( (VALUE) , (VALUE) \)',
    divmod_
)
