import sys

is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib

    _util = getattr(uacalc_lib, 'util')

    for _name in dir(_util):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_util, _name)
else:
    from org.uacalc.util import *
