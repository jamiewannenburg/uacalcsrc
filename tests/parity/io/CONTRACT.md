# org.uacalc.io Jython Compatibility Contract

This contract defines the parity target for `python/org/uacalc/io`: old Jython
scripts that import `org.uacalc.io` should run with minimal changes on CPython.
The compatibility surface is Java/Jython syntax, not the lower-level Rust or
Pythonic API.

## General Rules

- Parity tests must import and call `org.uacalc.io` using Java/Jython names:
  class names, constructors, static methods, and camelCase methods.
- Snake_case module functions may exist as CPython conveniences, but they do not
  satisfy this contract by themselves.
- Tests must fail if a required camelCase alias or Java-style constructor is
  missing.
- CPython may support additional inputs that Jython does not support, such as
  Python file-like objects, `io` buffers, `bytes`, `str` content, or Unicode
  operation symbols. Those extension cases belong in `python/uacalc/tests`, not
  in Jython parity tests for now.
- For failure cases, exact error text is not part of the contract. If CPython
  fails on a malformed or unsupported parity fixture, Jython should fail too.
  CPython may accept more cases than Jython.

## Semantic Algebra Comparison

When a method returns an algebra, compare a normalized semantic summary:

- algebra name
- cardinality
- algebra kind/type when available
- operation symbols
- operation arities
- operation tables, normalized to lists of integers

The similarity type is covered by operation symbols plus arities. For lists of
algebras, compare the ordered list of these summaries.

When comparing XML output, normalize XML before comparison. Do not require
byte-for-byte equality unless a later contract explicitly says so.

## Fixtures

- Use existing example algebra files from `resources/algebras`.
- Use existing Mace4 files from `resources/mace4`.
- Create multi-algebra list fixtures directly in `resources/algebras`.
- Create special algebra fixtures in `resources/special`, including saved
  examples for basic, product, quotient, subalgebra, and power algebras. These
  fixtures should be generated with Jython when practical, then read by both
  Jython and CPython and compared semantically.

## AlgebraIO

Required Java/Jython syntax:

- `AlgebraIO.readAlgebraFile(path_or_file)`
- `AlgebraIO.readAlgebraFromStream(stream)`
- `AlgebraIO.readAlgebraListFile(path_or_file)`
- `AlgebraIO.readAlgebraListFromStream(stream)`
- `AlgebraIO.convertToXML(path_or_file)`
- `AlgebraIO.writeAlgebraFile(algebra, path_or_file)`
- `AlgebraIO.writeAlgebraFile(algebra, path_or_file, oldStyle)`

Compatibility requirements:

- `readAlgebraFile`: semantic parity using examples from `resources/algebras`.
- `readAlgebraFromStream`: semantic parity. CPython should support everything
  that works in Jython, plus Python file-like objects, `io` buffers, `bytes`,
  and `str` inputs.
- `readAlgebraListFile`: semantic parity using a checked-in multi-algebra
  fixture in `resources/algebras`.
- `readAlgebraListFromStream`: same semantic parity and input policy as
  `readAlgebraFromStream`.
- `convertToXML`: semantic parity by normalized XML comparison.
- `writeAlgebraFile` without `oldStyle`: semantic parity by normalized XML
  comparison.
- `writeAlgebraFile` with `oldStyle`: semantic parity by normalized XML
  comparison for both `oldStyle=True` and `oldStyle=False`.

Out of scope:

- `AlgebraIO.parseLine`
- `AlgebraIO.readProjectivePlane`
- `AlgebraIO.readOp`
- `AlgebraIO.readDepth2List`
- `AlgebraIO.main`

## AlgebraReader

Required Java/Jython syntax:

- `AlgebraReader(path_or_file)`
- `AlgebraReader(stream)`
- `reader.readAlgebraFile()`
- `reader.readAlgebraFromStream()`
- `reader.readAlgebraListFile()`
- `reader.readAlgebraListFromStream()`

Compatibility requirements:

- Constructors must support old Jython-style instantiation, but constructor
  behavior does not need direct tests beyond use by the read methods.
- Read methods have the same semantic parity requirements as the corresponding
  `AlgebraIO` methods.
- Algebra files covering basic, product, quotient, subalgebra, and power
  algebras must be readable by both Jython and CPython and compared
  semantically.

Out of scope:

- SAX handler methods such as `characters`, `startElement`, and `endElement`
- direct constant comparison for `BASIC`, `PRODUCT`, `QUOTIENT`, `SUBALGEBRA`,
  `POWER`, and `EMPTY_STRING`
- `AlgebraReader.main`

## AlgebraWriter

Required Java/Jython syntax:

- `AlgebraWriter(algebra, path_or_writer)`
- `writer.writeAlgebraXML()`
- `writer.writeAlgebra()`
- `writer.writeBasicAlgebra()`

Compatibility requirements:

- Constructors must support old Jython-style instantiation, but constructor
  behavior does not need direct tests beyond use by the write methods.
- Writer methods should be tested semantically by normalized XML comparison.
- Where practical, CPython may also support Python file-like writers.

Out of scope:

- direct comparison of public XML tag constants
- `AlgebraWriter.main`

## BadAlgebraFileException

Compatibility requirements:

- Semantic parity only. Exact error text is not part of the contract.
- The exception should be catchable in CPython in the same practical situations
  where old Jython scripts can catch `BadAlgebraFileException`.
- If CPython fails on a parity IO case, Jython should fail too. CPython may
  support more valid inputs than Jython.

## Mace4Reader

Required Java/Jython syntax:

- `Mace4Reader(stream)`
- `reader.parseAlgebra()`
- `reader.parseAlgebraList()`

Compatibility requirements:

- `Mace4Reader` is important for parity. CPython should parse everything that
  Jython parses, and may parse more.
- `parseAlgebra` and `parseAlgebraList` must be tested semantically using files
  in `resources/mace4`, including single-interpretation files and files
  containing lists of interpretations.
- Malformed or incomplete inputs may be tested semantically by failure/no-failure
  behavior. Exact exception messages and line/column text are not part of the
  contract.

Out of scope:

- `Mace4Reader.isOrdinaryCharacter`
- `Mace4Reader.isSpecialCharacter`

## ExtFileFilter

`ExtFileFilter` is out of scope for this IO parity contract.

## JSONChannel

`JSONChannel` is out of scope for this IO parity contract.
