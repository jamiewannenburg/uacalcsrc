import sys

is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib

    _element = getattr(uacalc_lib, 'element')

    for _name in dir(_element):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_element, _name)
else:
    from org.uacalc.element import *
