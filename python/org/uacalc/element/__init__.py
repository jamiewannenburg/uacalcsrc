def _load_from_uacalc_lib() -> None:
    import uacalc_lib as _uacalc_lib

    _element = getattr(_uacalc_lib, 'element')
    g = globals()
    for _name in dir(_element):
        if not _name.startswith('_'):
            g[_name] = getattr(_element, _name)


if __import__('sys').platform.startswith('java'):
    from org.uacalc.element import *  # noqa: F403
else:
    _load_from_uacalc_lib()
    del _load_from_uacalc_lib
