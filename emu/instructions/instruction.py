def paramcount(count):
    """@paramcount(count) decorator generator, to ensure
       that a instruction has the right amount of parameters
    """
    def pc_generator(old_function):
        """@paramcount decorator"""
        def new_function(m, params):
            if len(params) != count:
                print(f'err: invalid paramater count ({count}, got {len(params)}')
                quit()

            old_function(m, params)
        return new_function
    return pc_generator
