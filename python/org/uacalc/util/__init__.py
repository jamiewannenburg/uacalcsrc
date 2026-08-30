import sys

if sys.platform.startswith('java'):
    from org.uacalc.util import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _util = getattr(_uacalc_lib, 'util')

    for _name in dir(_util):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_util, _name)

    if 'ArrayIncrementorImpl' in globals():
        globals()['ArrayIncrementor'] = globals()['ArrayIncrementorImpl']
    if 'LongListUtils' in globals():
        globals()['LongList'] = globals()['LongListUtils']

    del _uacalc_lib, _util

del sys
