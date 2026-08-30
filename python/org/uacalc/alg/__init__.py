import sys
is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib
    _alg = getattr(uacalc_lib, 'alg')

    # Export everything from _alg to this module
    for _name in dir(_alg):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_alg, _name)

    # Per-class camelCase aliases — kept in sync with file-level contracts:
    #   jython_contracts/org.uacalc.alg.BasicAlgebra.yaml
    #   jython_contracts/org.uacalc.alg.SmallAlgebra.yaml
    # Package contract org.uacalc.alg.yaml is intentionally thin (re-export only).
    _CLASS_ALIASES = {
        'SmallAlgebra': {
            'getUniverseList': 'get_universe_list',
            'elementIndex': 'element_index',
            'algebraType': 'algebra_type',
            'resetConAndSub': 'reset_con_and_sub',
            'getName': 'name',
        },
        'BasicAlgebra': {
            'getUniverseList': 'get_universe_list',
            'elementIndex': 'element_index',
            'algebraType': 'algebra_type',
            'resetConAndSub': 'reset_con_and_sub',
            'getName': 'name',
        },
    }

    def _apply_class_aliases():
        for class_name, aliases in _CLASS_ALIASES.items():
            cls = globals().get(class_name)
            if cls is None:
                continue
            for camel, snake in aliases.items():
                impl = getattr(cls, snake, None)
                if impl is not None:
                    setattr(cls, camel, impl)

    _apply_class_aliases()
else:
    # In Jython, import from the Java package
    from org.uacalc.alg import *
