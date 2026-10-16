"""Jython-style wrappers around ``uacalc_lib.io`` (CPython only)."""

from __future__ import annotations

import os
import shutil
from typing import Any, List, Optional, Union

import uacalc_lib as _uacalc_lib

from org.uacalc._exceptions import (
    FileNotFoundException,
    java_file_not_found_message,
    translate_io_error,
)

_io = getattr(_uacalc_lib, "io")
_LibAlgebraReader = _io.AlgebraReader
_LibAlgebraWriter = _io.AlgebraWriter
_LibMace4Reader = _io.Mace4Reader
_LibBadAlgebraFileException = _io.BadAlgebraFileException


def _coerce_path(path_or_file: Any) -> str:
    if isinstance(path_or_file, (str, os.PathLike)):
        return os.fspath(path_or_file)
    if hasattr(path_or_file, "name") and isinstance(getattr(path_or_file, "name", None), str):
        return path_or_file.name
    raise TypeError(
        "expected a path string or path-like object, got {!r}".format(type(path_or_file))
    )


_FREE_TYPE_NAMES = ("PyFreeAlgebra", "FreeAlgebra")
_BASIC_TYPE_NAMES = ("PyBasicAlgebra", "BasicAlgebra")


def _algebra_type_name(alg: Any) -> str:
    return type(alg).__name__


def _write_algebra_xml(algebra: Any, path: str) -> None:
    """Dispatch type-specific XML writers. FreeAlgebra keeps coordinate tuples."""
    from org.uacalc.io._typed_xml import write_typed_algebra_xml

    alg = getattr(algebra, "_inner", algebra)
    if write_typed_algebra_xml(alg, path):
        return None
    if _algebra_type_name(alg) not in _BASIC_TYPE_NAMES:
        conv = getattr(alg, "to_basic_algebra", None)
        if callable(conv):
            alg = conv()
    return _LibAlgebraWriter.write_algebra_xml_to_file(alg, path)


def _raise_if_missing(path: str) -> None:
    """Raise Java ``FileNotFoundException`` before the library tries to parse.

    Java ``SAXParser.parse(File)`` uses the absolute path in
    ``java.io.FileNotFoundException: <abspath> (No such file or directory)``.
    The parity harness compares ``str(exc)`` and strips the
    ``java.io.FileNotFoundException: `` prefix, so the shim message is the
    ``getMessage()`` form ``<abspath> (No such file or directory)``.
    """
    if os.path.isfile(path):
        return
    raise FileNotFoundException(java_file_not_found_message(os.path.abspath(path)))


def _coerce_stream_bytes(stream: Any) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, str):
        return stream.encode("utf-8")
    if hasattr(stream, "read"):
        data = stream.read()
        if isinstance(data, str):
            return data.encode("utf-8")
        return bytes(data)
    raise TypeError(
        "expected bytes, str, or a readable stream, got {!r}".format(type(stream))
    )


class AlgebraIO:
    """Static helpers matching ``org.uacalc.io.AlgebraIO``."""

    @staticmethod
    def readAlgebraFile(path_or_file: Any) -> Any:
        # Use AlgebraReader so description and other SAX fields survive (the
        # module-level read_algebra_file rebuilds a bare BasicAlgebra).
        path = _coerce_path(path_or_file)
        _raise_if_missing(path)
        return AlgebraReader(path).readAlgebraFile()

    @staticmethod
    def readAlgebraFromStream(stream: Any) -> Any:
        return AlgebraReader(_coerce_stream_bytes(stream)).readAlgebraFromStream()

    @staticmethod
    def readAlgebraListFile(path_or_file: Any) -> List[Any]:
        # Java's SAX list reader keeps only the last algebra (known Java bug).
        # The org wrapper deliberately returns every algebra in the list.
        return _io.read_algebra_list_file(_coerce_path(path_or_file))

    @staticmethod
    def readAlgebraListFromStream(stream: Any) -> Any:
        return _io.read_algebra_list_from_stream(_coerce_stream_bytes(stream))

    @staticmethod
    def convertToXML(path_or_file: Any) -> None:
        # Java ExtFileFilter.splitOffExtension uses File.getName(), then writes
        # <basename>.xml in the current working directory. uacalc_lib writes
        # beside the source path; relocate the library output to match Java.
        path = _coerce_path(path_or_file)
        name, ext = _io.ExtFileFilter.split_off_extension(path)
        if not name or ext is None or str(ext).lower() != "alg":
            return None
        try:
            _io.convert_to_xml(path)
        except Exception as exc:
            translate_io_error(exc, path=path)
        produced = os.path.join(os.path.dirname(os.path.abspath(path)), name + ".xml")
        java_dest = os.path.join(os.getcwd(), name + ".xml")
        if os.path.abspath(produced) != os.path.abspath(java_dest) and os.path.isfile(
            produced
        ):
            shutil.move(produced, java_dest)

    @staticmethod
    def parseLine(line: Any) -> int:
        return int(_io.parse_line(str(line)))

    @staticmethod
    def writeAlgebraFile(algebra: Any, path_or_file: Any, oldStyle: Optional[bool] = None) -> None:
        path = _coerce_path(path_or_file)
        alg = getattr(algebra, "_inner", algebra)
        use_old_style = bool(oldStyle) if oldStyle is not None else False
        if use_old_style:
            if _algebra_type_name(alg) not in _BASIC_TYPE_NAMES:
                conv = getattr(alg, "to_basic_algebra", None)
                if callable(conv):
                    alg = conv()
            return _io.write_algebra_file_with_style(alg, path, True)
        # Java AlgebraIO.writeAlgebraFile writes XML to the given path whenever
        # the file has an extension (including .ua). uacalc_lib.write_algebra_file
        # appends ".xml" for non-.xml suffixes, so use AlgebraWriter instead.
        return _write_algebra_xml(alg, path)


class AlgebraReader:
    """Instance reader matching ``org.uacalc.io.AlgebraReader``."""

    def __init__(self, path_or_stream: Any) -> None:
        if isinstance(path_or_stream, (bytes, bytearray)):
            self._path: Optional[str] = None
            self._stream_data = bytes(path_or_stream)
            self._inner = _LibAlgebraReader.new_from_stream(self._stream_data)
        elif hasattr(path_or_stream, "read"):
            self._path = None
            self._stream_data = _coerce_stream_bytes(path_or_stream)
            self._inner = _LibAlgebraReader.new_from_stream(self._stream_data)
        else:
            # Java AlgebraReader(String/File) is always a filename. A missing
            # path must not be treated as XML stream content.
            self._path = _coerce_path(path_or_stream)
            self._stream_data = None
            if os.path.isfile(self._path):
                self._inner = _LibAlgebraReader.new_from_file(self._path)
            else:
                self._inner = None

    def readAlgebraFile(self) -> Any:
        return self.read_algebra_file()

    def read_algebra_file(self) -> Any:
        try:
            if self._path is not None:
                _raise_if_missing(self._path)
                if self._inner is None:
                    self._inner = _LibAlgebraReader.new_from_file(self._path)
                result = self._inner.read_algebra_file()
            else:
                result = self._inner.read_algebra_from_stream(self._stream_data)
        except Exception as exc:
            translate_io_error(
                exc, path=self._path, stream_text=self._stream_text()
            )
        if result is None:
            raise ValueError("no algebra read from source")
        from org.uacalc.io._typed_xml import rebuild_typed_algebra

        xml_text = None
        if self._path is not None and os.path.isfile(self._path):
            with open(self._path) as handle:
                xml_text = handle.read()
        elif self._stream_data:
            try:
                xml_text = bytes(self._stream_data).decode("utf-8")
            except Exception:
                xml_text = None
        return rebuild_typed_algebra(result, xml_text)

    def readAlgebraFromStream(self) -> Any:
        return self.read_algebra_from_stream()

    def read_algebra_from_stream(self) -> Any:
        if self._stream_data is None:
            raise ValueError("reader was not constructed from a stream")
        try:
            result = self._inner.read_algebra_from_stream(self._stream_data)
        except Exception as exc:
            translate_io_error(exc, stream_text=self._stream_text())
        if result is None:
            raise ValueError("no algebra read from stream")
        from org.uacalc.io._typed_xml import rebuild_typed_algebra

        xml_text = None
        if self._stream_data:
            try:
                xml_text = bytes(self._stream_data).decode("utf-8")
            except Exception:
                xml_text = None
        return rebuild_typed_algebra(result, xml_text)

    def _stream_text(self) -> Optional[str]:
        if not self._stream_data:
            return None
        try:
            return bytes(self._stream_data).decode("utf-8", "replace")
        except Exception:
            return None

    def readAlgebraListFile(self) -> List[Any]:
        return self.read_algebra_list_file()

    def read_algebra_list_file(self) -> List[Any]:
        # Java AlgebraReader.readAlgebraListFile keeps only the last algebra
        # (known Java bug). Return the full list, matching AlgebraIO.
        if self._path is not None:
            return self._inner.read_algebra_list_from_file(self._path)
        return self._inner.read_algebra_list_from_stream(self._stream_data)

    def readAlgebraListFromStream(self) -> List[Any]:
        return self.read_algebra_list_from_stream()

    def read_algebra_list_from_stream(self) -> List[Any]:
        if self._stream_data is None:
            raise ValueError("reader was not constructed from a stream")
        return self._inner.read_algebra_list_from_stream(self._stream_data)


class AlgebraWriter:
    """Writer matching ``org.uacalc.io.AlgebraWriter`` instance API."""

    def __init__(self, algebra: Any, path_or_writer: Any) -> None:
        self._algebra = getattr(algebra, "_inner", algebra)
        if hasattr(path_or_writer, "write"):
            raise NotImplementedError(
                "AlgebraWriter with a custom writer is not bound in uacalc_lib"
            )
        self._path = _coerce_path(path_or_writer)
        # Java `new FileWriter(file)` creates/truncates; content is buffered
        # in the PrintWriter and is not flushed by writeAlgebra.
        open(self._path, "w").close()

    def writeAlgebraXML(self) -> None:
        return self.write_algebra_xml()

    def write_algebra_xml(self) -> None:
        return _write_algebra_xml(self._algebra, self._path)

    def writeAlgebra(self) -> None:
        return self.write_algebra()

    def write_algebra(self) -> None:
        # Java writes into an unflushed PrintWriter; the destination file
        # stays empty until writeAlgebraXML closes the stream.
        return None

    def writeBasicAlgebra(self) -> None:
        return self.write_basic_algebra()

    def write_basic_algebra(self) -> None:
        # Same unflushed PrintWriter as writeAlgebra.
        return None

    def flush(self) -> None:
        """No-op: Java AlgebraWriter never flushes the output stream."""
        return None


class Mace4Reader:
    """Mace4 parser matching ``org.uacalc.io.Mace4Reader``.

    Jython constructs ``Mace4Reader(stream)`` and calls ``parseAlgebra()``.
    Static helpers from ``uacalc_lib.io.Mace4Reader`` are re-exported so callers
    can use either the Java constructor or the binding factory methods.
    """

    new_from_file = staticmethod(_LibMace4Reader.new_from_file)
    new_from_stream = staticmethod(_LibMace4Reader.new_from_stream)
    parse_algebra_from_file = staticmethod(_LibMace4Reader.parse_algebra_from_file)

    @staticmethod
    def isOrdinaryCharacter(c: Any) -> bool:
        return bool(_LibMace4Reader.is_ordinary_character(c if isinstance(c, str) else chr(int(c))))

    @staticmethod
    def isSpecialCharacter(c: Any) -> bool:
        return bool(_LibMace4Reader.is_special_character(c if isinstance(c, str) else chr(int(c))))

    @staticmethod
    def open(path: Any) -> "Mace4Reader":
        """Open a path like Java ``Mace4Reader(new FileInputStream(path))``."""
        filename = _coerce_path(path)
        try:
            fh = open(filename, "rb")
        except FileNotFoundError as exc:
            raise FileNotFoundException(
                java_file_not_found_message(filename, exc)
            ) from exc
        try:
            return Mace4Reader(fh)
        finally:
            fh.close()

    def __init__(self, stream: Any) -> None:
        self._data = _coerce_stream_bytes(stream)
        self._inner = _LibMace4Reader.new_from_stream(self._data)

    def parseAlgebra(self) -> Any:
        return self.parse_algebra()

    def parse_algebra(self) -> Any:
        result = self._inner.parse_algebra_from_stream(self._data)
        if result is None:
            raise ValueError("no algebra parsed from Mace4 stream")
        return result

    def parseAlgebraList(self) -> List[Any]:
        return self.parse_algebra_list()

    def parse_algebra_list(self) -> List[Any]:
        return self._inner.parse_algebra_list_from_stream(self._data)


BadAlgebraFileException = _LibBadAlgebraFileException


def _filter_path(path_or_file: Any) -> str:
    if hasattr(path_or_file, "getName") and callable(path_or_file.getName):
        # Java File: ExtFileFilter uses File.getName() only.
        name = path_or_file.getName()
        return str(name) if name is not None else ""
    if hasattr(path_or_file, "getPath") and callable(path_or_file.getPath):
        return str(path_or_file.getPath())
    if isinstance(path_or_file, (str, os.PathLike)):
        return os.fspath(path_or_file)
    if hasattr(path_or_file, "name") and isinstance(getattr(path_or_file, "name", None), str):
        return path_or_file.name
    return str(path_or_file)


class ExtFileFilter:
    """Filter matching ``org.uacalc.io.ExtFileFilter``."""

    def __init__(self, desc: Any, exts_or_ext: Any) -> None:
        description = str(desc)
        if isinstance(exts_or_ext, str):
            self._inner = _io.ExtFileFilter.new_single(description, exts_or_ext)
        else:
            self._inner = _io.ExtFileFilter(description, [str(x) for x in list(exts_or_ext)])

    def accept(self, path_or_file: Any) -> bool:
        return bool(self._inner.accept(_filter_path(path_or_file)))

    def getDescription(self) -> str:
        return self._inner.get_description()

    def get_description(self) -> str:
        return self.getDescription()

    @staticmethod
    def getExtension(path_or_file: Any) -> Optional[str]:
        return _io.ExtFileFilter.get_extension(_filter_path(path_or_file))

    @staticmethod
    def get_extension(path_or_file: Any) -> Optional[str]:
        return ExtFileFilter.getExtension(path_or_file)

    @staticmethod
    def splitOffExtension(path_or_file: Any) -> Any:
        return _io.ExtFileFilter.split_off_extension(_filter_path(path_or_file))

    @staticmethod
    def split_off_extension(path_or_file: Any) -> Any:
        return ExtFileFilter.splitOffExtension(path_or_file)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ExtFileFilter):
            return NotImplemented
        return self._inner == other._inner

    def __hash__(self) -> int:
        return hash(self._inner)

    def __str__(self) -> str:
        return str(self._inner)

    def __repr__(self) -> str:
        return repr(self._inner)
