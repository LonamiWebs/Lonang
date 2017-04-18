"""Built-in functions"""
from variables import Variable
from functions import Function

def define_integer_to_string(c):
    """Defines the 'integer_to_string' built-in function.
        AX is used to pass the input parameter, number to convert,
        and is lost in the progress. Caller is responsibe to save it.

        Returns the Function header.
    """
    vname = '_v_itos'
    fname = '_f_itos'
    function = Function(fname, params=['ax'], returns=vname, mangle=False)

    # Early exit if it's already defined
    if fname in c.functions:
        return function

    maxlen = len(f'-{0x7FFF}$')
    c.add_variable(Variable(vname, f'byte[{maxlen}]', '?'))

    c.begin_function(function)
    c.add_code('''push bx
    push cx
    push dx
    push di

    xor cx, cx  ; Digit counter
    mov bx, 10  ; Cannot divide by inmediate
    lea di, _v_itos  ; Destination string index

    ; Special case, number is negative
    cmp ax, 0
    jge _f_itos_loop1

    mov [di], '-'
    inc di
    neg ax

_f_itos_loop1:
    ; DX is considered on division, reset it to zero
    xor dx, dx
    div bx
    add dl, '0'
    ; From less significant to most significant (use stack to reverse)
    push dx
    inc cx
    cmp ax, 0
    jg _f_itos_loop1

_f_itos_loop2:
    ; Reverse the stored digits back from the stack
    pop [di]
    inc di
    loop _f_itos_loop2

    ; Strings must end with the dollar sing
    mov [di], '$'

    pop di
    pop dx
    pop cx
    pop bx''')
    c.close_block()

    return function

def define_set_cursor(c):
    """Defines the 'setcursor' built-in function.
        DH contains the row and DL contains the column.

        Returns the Function header.
    """
    fname = '_f_setc'
    function = Function(fname, params=['dx'], mangle=False)

    # Early exit if it's already defined
    if fname in c.functions:
        return function

    c.begin_function(function)
    c.add_code('''push ax
    push bx
    mov ah, 2
    mov bh, 0
    int 10h
    pop bx
    pop ax''')
    c.close_block()

    return function


def define_tmp_variable(c, register):
    """Defines a temporary variable for the given
        register, to be used instead of the stack.

        Returns the name of the temporary variable.
    """
    vname = f'_v_tmp_{register}'
    if vname not in c.variables:
        # TODO Use utils to determine the size instead?
        size = 'byte' if register[-1] in 'hl' else 'short'
        c.add_variable(Variable(vname, size, '?'))

    return vname
