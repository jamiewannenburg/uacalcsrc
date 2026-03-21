import sys
is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib
    _alg = getattr(uacalc_lib, 'alg')
    
    # Export everything from _alg to this module
    for _name in dir(_alg):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_alg, _name)

    def monkey_patch_classes():
        # Patch Algebra to have camelCase aliases
        # This is done on the class itself
        try:
            # Check for main classes in globals which were just added
            if 'SmallAlgebra' in globals():
                cls = globals()['SmallAlgebra']
                cls.getUniverseList = cls.get_universe_list
                cls.elementIndex = cls.element_index
                cls.algebraType = cls.algebra_type
                cls.resetConAndSub = cls.reset_con_and_sub
                cls.getName = cls.name
                
            if 'BasicAlgebra' in globals():
                cls = globals()['BasicAlgebra']
                cls.getUniverseList = cls.get_universe_list
                cls.elementIndex = cls.element_index
                cls.algebraType = cls.algebra_type
                cls.resetConAndSub = cls.reset_con_and_sub
                cls.getName = cls.name
        except (AttributeError, NameError):
            pass

    # Call it when this module is imported
    monkey_patch_classes()
else:
    # In Jython, we should import from the Java package
    from org.uacalc.alg import *
