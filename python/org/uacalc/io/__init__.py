import sys

if sys.platform.startswith('java'):
    from org.uacalc.io import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _io = getattr(_uacalc_lib, 'io')

    AlgebraReader = _io.AlgebraReader
    AlgebraWriter = _io.AlgebraWriter
    BadAlgebraFileException = _io.BadAlgebraFileException
    ExtFileFilter = _io.ExtFileFilter
    Mace4Reader = _io.Mace4Reader

    parse_line = _io.parse_line
    read_algebra_file = _io.read_algebra_file
    read_algebra_from_stream = _io.read_algebra_from_stream
    read_algebra_list_file = _io.read_algebra_list_file
    read_algebra_list_from_stream = _io.read_algebra_list_from_stream
    convert_to_xml = _io.convert_to_xml
    write_algebra_file = _io.write_algebra_file
    write_algebra_file_with_style = _io.write_algebra_file_with_style
    read_projective_plane = _io.read_projective_plane
    read_projective_plane_from_stream = _io.read_projective_plane_from_stream

    class AlgebraIO:
        """Shim for ``org.uacalc.io.AlgebraIO`` static helpers; delegates to ``uacalc_lib.io``."""

        @staticmethod
        def readAlgebraFile(path):
            reader = AlgebraReader.new_from_file(path)
            return reader.read_algebra_file()

    class JSONChannel:
        """Placeholder for Java ``org.uacalc.io.JSONChannel`` (not yet bound in ``uacalc_lib``)."""

        def __init__(self, *_args, **_kwargs):
            raise NotImplementedError(
                "JSONChannel is not yet implemented in uacalc_lib; use Jython with uacalc.jar."
            )

    del _uacalc_lib, _io

del sys
