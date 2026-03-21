import sys
is_jython = sys.platform.startswith('java')

if not is_jython:
    import uacalc_lib
    # Access it as an attribute of the module, not a top-level import
    # which might be shadowed by standard 'io'
    _io = getattr(uacalc_lib, 'io')
    AlgebraReader = _io.AlgebraReader

    class AlgebraIO:
        @staticmethod
        def readAlgebraFile(path):
            reader = AlgebraReader.new_from_file(path)
            return reader.read_algebra_file()
else:
    from org.uacalc.io import AlgebraIO
