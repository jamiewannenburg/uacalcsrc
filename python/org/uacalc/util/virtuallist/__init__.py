import sys

if sys.platform.startswith('java'):
    from org.uacalc.util.virtuallist import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _util = getattr(_uacalc_lib, 'util')
    LongList = getattr(_util, 'LongListUtils')
    TupleWithMin = getattr(_util, 'TupleWithMin')
    VirtualLists = getattr(_util, 'VirtualLists')

    del _uacalc_lib, _util

del sys
