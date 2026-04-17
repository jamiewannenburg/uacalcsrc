import sys
is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib
    _lat = getattr(uacalc_lib, 'lat')

    for _name in dir(_lat):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_lat, _name)
else:
    from org.uacalc.lat import *
