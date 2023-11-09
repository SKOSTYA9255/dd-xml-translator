# Courtesy of https://stackoverflow.com/a/16589622
def full_stack()->str:
    """Prints the full stack trace when called. 
    The stacktraces is very similar to the stacktraces produced by Python on uncaught exceptions.
    Should be used in a catch statement.

    Returns:
        str: List of strings (ready for printing) showing the full stack trace
    """
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr