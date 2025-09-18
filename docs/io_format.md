# UACalc .ua File Format Documentation

## Overview

The .ua file format is an XML-based format for representing universal algebras, designed for compatibility with the Java UACalc implementation. This document describes the format specification, I/O operations, and usage examples.

## File Format Specification

### XML Structure

.ua files use a nested XML structure with the following hierarchy:

```xml
<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>algebra_name</algName>
    <desc>algebra_description</desc>
    <cardinality>n</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>operation_name</opName>
          <arity>k</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[i]">v0,v1,...,vm</row>
            ...
          </intArray>
        </opTable>
      </op>
      ...
    </operations>
  </basicAlgebra>
</algebra>
```

### Required Elements

- **`<algebra>`**: Root element containing the algebra definition
- **`<basicAlgebra>`**: Specifies the algebra type (currently only basic algebras are supported)
- **`<algName>`**: Name of the algebra (required)
- **`<cardinality>`**: Number of elements in the universe (required, must be positive)
- **`<operations>`**: Container for operation definitions (optional if no operations)

### Optional Elements

- **`<desc>`**: Description of the algebra (optional)

### Operation Definition

Each operation is defined with:

- **`<opSymbol>`**: Operation symbol information
  - **`<opName>`**: Name of the operation (required)
  - **`<arity>`**: Number of arguments the operation takes (required, must be non-negative)
- **`<opTable>`**: Operation table definition
  - **`<intArray>`**: Container for table rows
    - **`<row>`**: Individual table row with optional `r` attribute

### Operation Table Format

Operation tables are stored as comma-separated values in row elements:

#### Unary Operations (arity = 1)
```xml
<row r="[0]">result_for_input_0</row>
<row r="[1]">result_for_input_1</row>
...
```

#### Binary Operations (arity = 2)
```xml
<row r="[0]">result_0_0,result_0_1,result_0_2,...</row>
<row r="[1]">result_1_0,result_1_1,result_1_2,...</row>
...
```

#### Higher Arity Operations
For operations with arity > 2, the table uses Horner encoding where:
- Row index represents the first argument
- Column index represents the remaining arguments encoded as a single number

### Row Attributes

The `r` attribute in row elements indicates the first argument value:
- `r="[0]"` means the row corresponds to first argument = 0
- `r="[1]"` means the row corresponds to first argument = 1
- etc.

## I/O API Usage

### Basic Operations

#### Loading Algebras

```python
from uacalc import load_algebra

# Load a single algebra
algebra = load_algebra("path/to/algebra.ua")
print(f"Loaded algebra: {algebra.name}")
print(f"Cardinality: {algebra.cardinality()}")
print(f"Operations: {[op.symbol for op in algebra.operations]}")
```

#### Saving Algebras

```python
from uacalc import create_algebra, create_operation, save_algebra

# Create an algebra
algebra = create_algebra("test", [0, 1, 2])

# Add operations
op = create_operation("test_op", 1, [[0, 1], [1, 2], [2, 0]])
algebra.add_operation("test_op", op)

# Save to file
save_algebra(algebra, "output.ua")
```

#### Validation

```python
from uacalc import validate_ua_file

# Validate a file without loading
is_valid, errors = validate_ua_file("test.ua")
if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("File is valid")
```

### Advanced Operations

#### Safe Loading with Error Handling

```python
from uacalc import load_algebra_safe

# Load with error reporting
algebra, errors = load_algebra_safe("test.ua")
if algebra is None:
    print(f"Failed to load: {errors}")
else:
    print(f"Successfully loaded: {algebra.name}")
```

#### Batch Operations

```python
from uacalc import batch_load_algebras

# Load multiple files
file_paths = ["alg1.ua", "alg2.ua", "alg3.ua"]
results = batch_load_algebras(file_paths)

for file_path, (algebra, errors) in results.items():
    if algebra is None:
        print(f"Failed to load {file_path}: {errors}")
    else:
        print(f"Loaded {file_path}: {algebra.name}")
```

#### File Information

```python
from uacalc import get_algebra_info, list_ua_files

# Get information about a file
info = get_algebra_info("test.ua")
print(f"Name: {info.get('name', 'Unknown')}")
print(f"Cardinality: {info.get('cardinality', 'Unknown')}")
print(f"Operations: {info.get('operation_count', 0)}")
print(f"Valid: {info.get('valid', False)}")

# List .ua files in a directory
ua_files = list_ua_files("path/to/directory")
for file_path in ua_files:
    print(f"Found: {file_path}")
```

## Error Handling

### Error Types

The I/O module provides specific error classes for different failure modes:

- **`BadUAFileError`**: General .ua file errors
- **`InvalidOperationTableError`**: Operation table validation errors
- **`UnsupportedAlgebraTypeError`**: Unsupported algebra types
- **`XMLParsingError`**: XML parsing errors
- **`FileFormatError`**: File format errors

### Error Handling Examples

```python
from uacalc import load_algebra
from uacalc.errors import BadUAFileError, InvalidOperationTableError

try:
    algebra = load_algebra("test.ua")
except BadUAFileError as e:
    print(f"File error: {e}")
    print(f"File path: {e.file_path}")
except InvalidOperationTableError as e:
    print(f"Table error: {e}")
    print(f"Operation: {e.operation_name}")
    print(f"Expected size: {e.expected_size}")
    print(f"Actual size: {e.actual_size}")
```

## Validation Rules

### XML Structure Validation

- Root element must be `<algebra>`
- Must contain exactly one algebra type element (currently only `<basicAlgebra>`)
- All required elements must be present
- XML must be well-formed

### Algebra Metadata Validation

- `<algName>` must be present and non-empty
- `<cardinality>` must be a positive integer
- `<desc>` is optional but must be a string if present

### Operation Validation

- Each operation must have `<opName>` and `<arity>` elements
- `<arity>` must be a non-negative integer
- Operation names must be non-empty strings

### Operation Table Validation

- Table must have exactly `cardinality` rows
- Each row must have the correct number of values based on arity
- All values must be integers in the range [0, cardinality-1]
- Values must be comma-separated
- Row attributes must be properly formatted

### Universe Validation

- Universe elements must be contiguous integers starting from 0
- All operation values must be within the universe range
- No duplicate or missing universe elements

## Examples

### Simple 2-Element Lattice

```xml
<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>lat2</algName>
    <desc>The 2 element lattice.</desc>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>join</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,1</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>meet</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,0</row>
            <row r="[1]">0,1</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>
```

### Diamond Lattice (M3)

```xml
<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>m3</algName>
    <desc>the diamond</desc>
    <cardinality>5</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>meet</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,0,0,0,0</row>
            <row r="[1]">0,1,0,0,1</row>
            <row r="[2]">0,0,2,0,2</row>
            <row r="[3]">0,0,0,3,3</row>
            <row r="[4]">0,1,2,3,4</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>join</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1,2,3,4</row>
            <row r="[1]">1,1,4,4,4</row>
            <row r="[2]">2,4,2,4,4</row>
            <row r="[3]">3,4,4,3,4</row>
            <row r="[4]">4,4,4,4,4</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>
```

## Compatibility Information

### Java UACalc Compatibility

The Python implementation is designed for full compatibility with Java UACalc:

- **File Format**: Identical XML structure and encoding
- **Operation Tables**: Same row-based format with `r` attributes
- **Metadata**: Preserves algebra names, descriptions, and cardinalities
- **Validation**: Compatible validation rules and error reporting

### Supported Algebra Types

Currently supported:
- **Basic Algebras**: Full support for basic algebras with arbitrary operations

Planned support:
- **Product Algebras**: Direct product of multiple algebras
- **Quotient Algebras**: Factor algebras by congruences
- **Subalgebras**: Subalgebras of existing algebras
- **Power Algebras**: Direct powers of algebras

### Limitations

- Only basic algebras are currently supported
- Universe must be contiguous integers starting from 0
- Operation tables must be complete (no partial functions)
- Maximum cardinality is limited by available memory

## Performance Considerations

### File Size

- Small algebras (< 10 elements): Load/save in milliseconds
- Medium algebras (10-100 elements): Load/save in seconds
- Large algebras (> 100 elements): May take significant time

### Memory Usage

- Memory usage scales with `cardinality^arity` for operation tables
- Large operation tables can consume significant memory
- Consider using batch operations for multiple files

### Validation Performance

- Basic validation is fast (milliseconds)
- Full table validation scales with table size
- Use `get_algebra_info()` for quick metadata extraction

## Troubleshooting

### Common Issues

1. **File Not Found**
   ```
   BadUAFileError: File not found: test.ua
   ```
   Solution: Check file path and permissions

2. **Invalid XML**
   ```
   XMLParsingError: Invalid XML in .ua file: ...
   ```
   Solution: Check XML syntax and structure

3. **Missing Elements**
   ```
   BadUAFileError: Missing <cardinality> element
   ```
   Solution: Ensure all required elements are present

4. **Invalid Table Size**
   ```
   InvalidOperationTableError: Operation table has wrong number of rows
   ```
   Solution: Check that table size matches `cardinality^arity`

5. **Values Outside Universe**
   ```
   InvalidOperationTableError: Value 5 is outside universe range [0, 4]
   ```
   Solution: Ensure all operation values are within universe range

### Debugging Tips

1. **Use validation first**:
   ```python
   is_valid, errors = validate_ua_file("test.ua")
   if not is_valid:
       print("Validation errors:", errors)
   ```

2. **Check file info**:
   ```python
   info = get_algebra_info("test.ua")
   print("File info:", info)
   ```

3. **Try safe loading**:
   ```python
   algebra, errors = load_algebra_safe("test.ua")
   if algebra is None:
       print("Load errors:", errors)
   ```

4. **Validate saved files**:
   ```python
   success, errors = save_algebra_validated(algebra, "output.ua")
   if not success:
       print("Save errors:", errors)
   ```

## Migration Guide

### From Old I/O API

If you were using the old I/O API, here are the changes:

1. **Error handling**: Use specific error classes instead of generic exceptions
2. **Validation**: Use `validate_ua_file()` for file validation
3. **Batch operations**: Use `batch_load_algebras()` for multiple files
4. **Safe operations**: Use `load_algebra_safe()` and `save_algebra_validated()`

### Example Migration

**Old code**:
```python
try:
    algebra = load_algebra("test.ua")
except Exception as e:
    print(f"Error: {e}")
```

**New code**:
```python
algebra, errors = load_algebra_safe("test.ua")
if algebra is None:
    print(f"Errors: {errors}")
```

## Future Enhancements

### Planned Features

1. **Additional Algebra Types**: Support for product, quotient, and subalgebras
2. **Compression**: Support for compressed .ua files
3. **Incremental Loading**: Load large algebras incrementally
4. **Schema Validation**: XML schema validation for .ua files
5. **Conversion Tools**: Convert between different algebra formats

### Extension Points

The I/O system is designed to be extensible:

- New algebra types can be added by implementing parsing functions
- Custom validation rules can be added
- Error handling can be customized
- File format variations can be supported

## References

- Java UACalc Documentation: [UACalc Java Documentation](http://uacalc.org/)
- XML Specification: [W3C XML 1.0](https://www.w3.org/TR/xml/)
- Universal Algebra: [Universal Algebra Textbook](https://math.hawaii.edu/~ralph/Classes/619/univ-algebra.pdf)
