"""
I/O module for UACalc algebra files.

This module provides functionality for reading and writing .ua files,
maintaining compatibility with the existing Java UACalc implementation.
The .ua format uses XML with nested structure for algebra definitions.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional, Any
import logging
import re

from . import Algebra, Operation, create_algebra, create_operation
from .errors import (
    UACalcError, BadUAFileError, InvalidOperationTableError, 
    UnsupportedAlgebraTypeError, XMLParsingError, FileFormatError,
    map_xml_error, map_io_error
)

logger = logging.getLogger(__name__)

def load_algebra(file_path: Union[str, Path]) -> Algebra:
    """
    Load an algebra from a .ua file.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Algebra object loaded from the file
        
    Raises:
        BadUAFileError: If the file cannot be parsed or is invalid
        InvalidOperationTableError: If operation tables are malformed
        UnsupportedAlgebraTypeError: If algebra type is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise BadUAFileError(f"File not found: {file_path}", file_path=str(file_path))
    
    if file_path.suffix.lower() != '.ua':
        raise FileFormatError(
            f"File must have .ua extension: {file_path}", 
            file_path=str(file_path),
            expected_format=".ua",
            actual_format=file_path.suffix
        )
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return _parse_ua_content(content, file_path.name, str(file_path))
        
    except (BadUAFileError, InvalidOperationTableError, UnsupportedAlgebraTypeError):
        raise
    except Exception as e:
        raise map_io_error(e, str(file_path))

def save_algebra(algebra: Algebra, file_path: Union[str, Path]) -> None:
    """
    Save an algebra to a .ua file.
    
    Args:
        algebra: Algebra object to save
        file_path: Path where to save the .ua file
        
    Raises:
        BadUAFileError: If the algebra cannot be saved
    """
    file_path = Path(file_path)
    
    try:
        content = _generate_ua_content(algebra)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        raise map_io_error(e, str(file_path))

def _parse_ua_content(content: str, filename: str, file_path: str) -> Algebra:
    """Parse the content of a .ua file."""
    try:
        # Remove any BOM and normalize line endings
        content = content.replace('\ufeff', '').replace('\r\n', '\n')
        
        # Parse XML content
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise map_xml_error(e, file_path)
        
        # Validate basic XML structure
        _validate_xml_structure(root, file_path)
        
        # Parse algebra based on type
        algebra_elem = root.find('basicAlgebra')
        if algebra_elem is not None:
            return _parse_basic_algebra(algebra_elem, file_path)
        
        # Check for other algebra types
        for alg_type in ['productAlgebra', 'quotientAlgebra', 'subalgebra', 'powerAlgebra']:
            if root.find(alg_type) is not None:
                raise UnsupportedAlgebraTypeError(
                    f"Algebra type '{alg_type}' is not yet supported", 
                    file_path=file_path,
                    algebra_type=alg_type,
                    supported_types=['basicAlgebra']
                )
        
        raise BadUAFileError(
            "No supported algebra type found in file", 
            file_path=file_path
        )
        
    except (BadUAFileError, InvalidOperationTableError, UnsupportedAlgebraTypeError, XMLParsingError):
        raise
    except Exception as e:
        raise BadUAFileError(f"Unexpected error parsing .ua file: {e}", file_path=file_path) from e

def _parse_basic_algebra(algebra_elem: ET.Element, file_path: str) -> Algebra:
    """Parse a basic algebra from XML element."""
    try:
        # Extract algebra name
        alg_name_elem = algebra_elem.find('algName')
        if alg_name_elem is None:
            raise BadUAFileError("Missing <algName> element", file_path=file_path)
        alg_name = alg_name_elem.text or "unnamed"
        
        # Extract description (optional)
        desc_elem = algebra_elem.find('desc')
        desc = desc_elem.text if desc_elem is not None else ""
        
        # Extract cardinality
        cardinality_elem = algebra_elem.find('cardinality')
        if cardinality_elem is None:
            raise BadUAFileError("Missing <cardinality> element", file_path=file_path)
        
        try:
            cardinality = int(cardinality_elem.text)
        except (ValueError, TypeError):
            raise BadUAFileError(
                f"Invalid cardinality value: {cardinality_elem.text}", 
                file_path=file_path
            )
        
        if cardinality <= 0:
            raise BadUAFileError(
                f"Cardinality must be positive, got: {cardinality}", 
                file_path=file_path
            )
        
        # Create universe
        universe = list(range(cardinality))
        
        # Create algebra
        algebra = create_algebra(alg_name, universe)
        
        # Preserve description metadata
        try:
            setattr(algebra, "description", desc)
        except (AttributeError, TypeError):
            # Some algebra objects may not support dynamic attributes
            pass
        
        # Parse operations
        operations_elem = algebra_elem.find('operations')
        if operations_elem is not None:
            for op_elem in operations_elem.findall('op'):
                operation = _parse_operation(op_elem, cardinality, file_path)
                algebra.add_operation(operation.symbol, operation)
        
        return algebra
        
    except (BadUAFileError, InvalidOperationTableError):
        raise
    except Exception as e:
        raise BadUAFileError(f"Error parsing basic algebra: {e}", file_path=file_path) from e

def _parse_operation(op_elem: ET.Element, cardinality: int, file_path: str) -> Operation:
    """Parse an operation from XML element."""
    try:
        # Extract operation symbol information
        op_symbol_elem = op_elem.find('opSymbol')
        if op_symbol_elem is None:
            raise BadUAFileError("Missing <opSymbol> element", file_path=file_path)
        
        op_name_elem = op_symbol_elem.find('opName')
        if op_name_elem is None:
            raise BadUAFileError("Missing <opName> element", file_path=file_path)
        op_name = op_name_elem.text or "unnamed"
        
        arity_elem = op_symbol_elem.find('arity')
        if arity_elem is None:
            raise BadUAFileError("Missing <arity> element", file_path=file_path)
        
        try:
            arity = int(arity_elem.text)
        except (ValueError, TypeError):
            raise BadUAFileError(
                f"Invalid arity value: {arity_elem.text}", 
                file_path=file_path
            )
        
        if arity < 0:
            raise BadUAFileError(
                f"Arity must be non-negative, got: {arity}", 
                file_path=file_path
            )
        
        # Parse operation table
        op_table_elem = op_elem.find('opTable')
        if op_table_elem is None:
            raise BadUAFileError("Missing <opTable> element", file_path=file_path)
        
        table = _parse_operation_table(op_table_elem, arity, cardinality, op_name, file_path)
        
        # Create operation with explicit cardinality
        from . import create_operation_with_size
        return create_operation_with_size(op_name, arity, table, cardinality)
        
    except (BadUAFileError, InvalidOperationTableError):
        raise
    except Exception as e:
        raise BadUAFileError(f"Error parsing operation: {e}", file_path=file_path) from e

def _parse_operation_table(op_table_elem: ET.Element, arity: int, cardinality: int, 
                          op_name: str, file_path: str) -> List[List[int]]:
    """Parse operation table from XML element."""
    try:
        int_array_elem = op_table_elem.find('intArray')
        if int_array_elem is None:
            raise InvalidOperationTableError(
                "Missing <intArray> element", 
                file_path=file_path,
                operation_name=op_name,
                expected_size=cardinality ** arity
            )
        
        # Calculate expected table size
        expected_size = cardinality ** arity
        
        # Parse rows
        rows = []
        for row_elem in int_array_elem.findall('row'):
            row_text = row_elem.text or ""
            row_values = _parse_row_values(row_text, cardinality, op_name, file_path)
            rows.append(row_values)
        
        # Validate table size - use 1 if arity <= 1 else cardinality^(arity-1)
        expected_row_count = 1 if arity <= 1 else (cardinality ** (arity - 1))
        if len(rows) != expected_row_count:
            raise InvalidOperationTableError(
                f"Operation table has wrong number of rows: expected {expected_row_count}, got {len(rows)}", 
                file_path=file_path,
                operation_name=op_name,
                expected_size=expected_size,
                actual_size=len(rows)
            )
        
        # Validate each row - use 1 if arity == 0, else cardinality
        for i, row in enumerate(rows):
            if arity == 0:
                expected_row_size = 1
            else:
                expected_row_size = cardinality
            
            if len(row) != expected_row_size:
                raise InvalidOperationTableError(
                    f"Row {i} has wrong size: expected {expected_row_size}, got {len(row)}", 
                    file_path=file_path,
                    operation_name=op_name,
                    row_index=i,
                    expected_size=expected_row_size,
                    actual_size=len(row)
                )
        
        # Convert to flat table format
        if arity == 0:
            # Constant operation
            return [[rows[0][0]]]
        elif arity == 1:
            # Unary operation - single row contains all function values
            return [[i, rows[0][i]] for i in range(cardinality)]
        else:
            # Multi-ary operation - flatten the table
            flat_table = []
            for args in _generate_combinations(list(range(cardinality)), arity):
                result = _get_table_value(rows, args, cardinality, arity)
                flat_table.append(args + [result])
            return flat_table
        
    except (BadUAFileError, InvalidOperationTableError):
        raise
    except Exception as e:
        raise InvalidOperationTableError(
            f"Error parsing operation table: {e}", 
            file_path=file_path,
            operation_name=op_name
        ) from e

def _parse_row_values(row_text: str, cardinality: int, op_name: str, file_path: str) -> List[int]:
    """Parse comma-separated values from a row."""
    try:
        # Split by comma and convert to integers
        values = []
        for value_str in row_text.split(','):
            value_str = value_str.strip()
            if not value_str:
                continue
            
            try:
                value = int(value_str)
            except ValueError:
                raise InvalidOperationTableError(
                    f"Invalid value in operation table: {value_str}", 
                    file_path=file_path,
                    operation_name=op_name
                )
            
            if value < 0 or value >= cardinality:
                raise InvalidOperationTableError(
                    f"Value {value} is outside universe range [0, {cardinality-1}]", 
                    file_path=file_path,
                    operation_name=op_name
                )
            
            values.append(value)
        
        return values
        
    except (BadUAFileError, InvalidOperationTableError):
        raise
    except Exception as e:
        raise InvalidOperationTableError(
            f"Error parsing row values: {e}", 
            file_path=file_path,
            operation_name=op_name
        ) from e

def _get_table_value(rows: List[List[int]], args: List[int], cardinality: int, arity: int) -> int:
    """Get value from operation table for given arguments."""
    if arity == 0:
        return rows[0][0]
    elif arity == 1:
        # For unary operations, we have 1 row with all values
        return rows[0][args[0]]
    else:
        # For multi-ary operations, use Horner encoding
        row_index = 0
        for i in range(arity - 1):
            row_index = row_index * cardinality + args[i]
        col_index = args[arity - 1]
        return rows[row_index][col_index]

def _generate_combinations(elements: List[int], length: int) -> List[List[int]]:
    """Generate all combinations of elements with given length."""
    if length == 0:
        return [[]]
    
    if length == 1:
        return [[x] for x in elements]
    
    result = []
    for elem in elements:
        for combo in _generate_combinations(elements, length - 1):
            result.append([elem] + combo)
    
    return result

def _generate_ua_content(algebra: Algebra) -> str:
    """Generate .ua file content from algebra."""
    # Create XML structure
    root = ET.Element('algebra')
    
    # Generate basic algebra content
    basic_algebra_elem = _generate_basic_algebra_xml(algebra)
    root.append(basic_algebra_elem)
    
    # Convert to string with proper formatting
    xml_str = ET.tostring(root, encoding='unicode')
    
    # Add XML declaration
    xml_str = '<?xml version="1.0"?>\n' + xml_str
    
    # Format with indentation (handle Python 3.8 compatibility)
    if hasattr(ET, 'indent'):
        # Python 3.9+
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        xml_str = ET.tostring(root, encoding='unicode')
        xml_str = '<?xml version="1.0"?>\n' + xml_str
    else:
        # Manual indentation for older Python versions
        xml_str = _format_xml_manually(xml_str)
    
    return xml_str

def _generate_basic_algebra_xml(algebra: Algebra) -> ET.Element:
    """Generate XML for a basic algebra."""
    basic_algebra = ET.Element('basicAlgebra')
    
    # Add algebra name
    alg_name = ET.SubElement(basic_algebra, 'algName')
    alg_name.text = algebra.name
    
    # Add description if available
    if hasattr(algebra, 'description') and algebra.description:
        desc = ET.SubElement(basic_algebra, 'desc')
        desc.text = algebra.description
    
    # Add cardinality
    cardinality = ET.SubElement(basic_algebra, 'cardinality')
    cardinality.text = str(algebra.cardinality)
    
    # Add operations
    operations = ET.SubElement(basic_algebra, 'operations')
    for operation in algebra.operations():
        op_elem = _generate_operation_xml(operation, algebra.universe)
        operations.append(op_elem)
    
    return basic_algebra

def _generate_operation_xml(operation: Operation, universe: List[int]) -> ET.Element:
    """Generate XML for an operation."""
    op = ET.Element('op')
    
    # Add operation symbol
    op_symbol = ET.SubElement(op, 'opSymbol')
    op_name = ET.SubElement(op_symbol, 'opName')
    op_name.text = operation.symbol
    arity = ET.SubElement(op_symbol, 'arity')
    arity.text = str(operation.arity())
    
    # Add operation table
    op_table = ET.SubElement(op, 'opTable')
    int_array = ET.SubElement(op_table, 'intArray')
    
    # Generate table rows
    rows = _generate_operation_table_xml(operation, universe)
    for row in rows:
        int_array.append(row)
    
    return op

def _generate_operation_table_xml(operation: Operation, universe: List[int]) -> List[ET.Element]:
    """Generate operation table XML rows."""
    rows = []
    cardinality = len(universe)
    arity = operation.arity()
    
    if arity == 0:
        # Constant operation
        result = operation.value([])
        row = ET.Element('row')
        row.text = str(result)
        rows.append(row)
    elif arity == 1:
        # Unary operation - single row with all values
        row = ET.Element('row')
        values = []
        for i in range(cardinality):
            result = operation.value([i])
            values.append(str(result))
        row.text = ','.join(values)
        rows.append(row)
    else:
        # Multi-ary operation - use Horner encoding
        expected_rows = cardinality ** (arity - 1)
        for row_index in range(expected_rows):
            row = ET.Element('row')
            row.set('r', f'[{row_index}]')
            
            # Generate values for this row
            values = []
            for col_index in range(cardinality):
                # Reconstruct the full argument tuple from row and column indices
                args = []
                temp_row = row_index
                for pos in range(arity - 1):
                    args.append(temp_row % cardinality)
                    temp_row //= cardinality
                args.reverse()
                args.append(col_index)
                
                result = operation.value(args)
                values.append(str(result))
            
            row.text = ','.join(values)
            rows.append(row)
    
    return rows

def _format_xml_manually(xml_str: str) -> str:
    """Format XML with minidom-based pretty-printer fallback for Python < 3.9."""
    try:
        from xml.dom import minidom
        
        # Parse the XML string
        dom = minidom.parseString(xml_str)
        
        # Pretty print with 2-space indentation
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove the first line (XML declaration) and add our own
        lines = pretty_xml.split('\n')
        if lines and lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        # Add our XML declaration as the first line
        result = '<?xml version="1.0"?>\n' + '\n'.join(lines)
        
        return result
        
    except Exception:
        # Fallback to manual formatting if minidom fails
        lines = xml_str.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Decrease indent for closing tags
            if line.startswith('</'):
                indent_level -= 1
            
            # Add indentation
            formatted_line = '  ' * indent_level + line
            formatted_lines.append(formatted_line)
            
            # Increase indent for opening tags (but not self-closing)
            if line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)

def _validate_xml_structure(root: ET.Element, file_path: str) -> None:
    """Validate basic XML structure."""
    if root.tag != 'algebra':
        raise BadUAFileError(
            f"Root element must be 'algebra', got '{root.tag}'", 
            file_path=file_path
        )
    
    # Check for at least one algebra type
    algebra_types = ['basicAlgebra', 'productAlgebra', 'quotientAlgebra', 'subalgebra', 'powerAlgebra']
    found_types = [t for t in algebra_types if root.find(t) is not None]
    
    if not found_types:
        raise BadUAFileError(
            "No algebra type found in file", 
            file_path=file_path
        )

def validate_ua_file(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate a .ua file without loading it.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    file_path = Path(file_path)
    
    try:
        # Check file exists
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return False, errors
        
        # Check file extension
        if file_path.suffix.lower() != '.ua':
            errors.append(f"File must have .ua extension: {file_path}")
            return False, errors
        
        # Read and parse XML
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            errors.append(f"XML parsing error: {e}")
            return False, errors
        
        # Validate XML structure
        try:
            _validate_xml_structure(root, str(file_path))
        except BadUAFileError as e:
            errors.append(str(e))
            return False, errors
        
        # Validate algebra content
        basic_algebra = root.find('basicAlgebra')
        if basic_algebra is not None:
            alg_errors = _validate_basic_algebra(basic_algebra, str(file_path))
            errors.extend(alg_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Unexpected error during validation: {e}")
        return False, errors

def _validate_basic_algebra(algebra_elem: ET.Element, file_path: str) -> List[str]:
    """Validate basic algebra structure."""
    errors = []
    
    # Check required elements
    if algebra_elem.find('algName') is None:
        errors.append("Missing <algName> element")
    
    cardinality = None
    if algebra_elem.find('cardinality') is None:
        errors.append("Missing <cardinality> element")
    else:
        cardinality_elem = algebra_elem.find('cardinality')
        try:
            cardinality = int(cardinality_elem.text)
            if cardinality <= 0:
                errors.append(f"Cardinality must be positive, got: {cardinality}")
        except (ValueError, TypeError):
            errors.append(f"Invalid cardinality value: {cardinality_elem.text}")
    
    # Validate operations
    operations_elem = algebra_elem.find('operations')
    if operations_elem is not None:
        for op_elem in operations_elem.findall('op'):
            op_errors = _validate_operation(op_elem, cardinality, file_path)
            errors.extend(op_errors)
    
    return errors

def _validate_operation(op_elem: ET.Element, cardinality: Optional[int], file_path: str) -> List[str]:
    """Validate operation structure."""
    errors = []
    
    # Check operation symbol
    op_symbol = op_elem.find('opSymbol')
    if op_symbol is None:
        errors.append("Missing <opSymbol> element")
    else:
        if op_symbol.find('opName') is None:
            errors.append("Missing <opName> element")
        if op_symbol.find('arity') is None:
            errors.append("Missing <arity> element")
        else:
            try:
                arity = int(op_symbol.find('arity').text)
                if arity < 0:
                    errors.append(f"Arity must be non-negative, got: {arity}")
            except (ValueError, TypeError):
                errors.append(f"Invalid arity value: {op_symbol.find('arity').text}")
    
    # Check operation table
    op_table = op_elem.find('opTable')
    if op_table is None:
        errors.append("Missing <opTable> element")
    else:
        if op_table.find('intArray') is None:
            errors.append("Missing <intArray> element")
        else:
            # Get arity for table validation
            arity = None
            if op_symbol is not None and op_symbol.find('arity') is not None:
                try:
                    arity = int(op_symbol.find('arity').text)
                except (ValueError, TypeError):
                    pass
            
            # Get operation name for better error messages
            op_name = "unnamed"
            if op_symbol is not None and op_symbol.find('opName') is not None:
                op_name = op_symbol.find('opName').text or "unnamed"
            
            # Validate table if we have the necessary information
            if cardinality is not None and arity is not None:
                table_errors = _validate_operation_table(op_elem, cardinality, file_path)
                errors.extend(table_errors)
    
    return errors

def _validate_operation_table(op_elem: ET.Element, cardinality: int, file_path: str) -> List[str]:
    """Validate operation table structure and content."""
    errors = []
    
    # Get operation name and arity
    op_symbol = op_elem.find('opSymbol')
    if op_symbol is None:
        return errors
    
    op_name = "unnamed"
    if op_symbol.find('opName') is not None:
        op_name = op_symbol.find('opName').text or "unnamed"
    
    arity = None
    if op_symbol.find('arity') is not None:
        try:
            arity = int(op_symbol.find('arity').text)
        except (ValueError, TypeError):
            errors.append(f"Invalid arity value for operation '{op_name}': {op_symbol.find('arity').text}")
            return errors
    
    if arity is None:
        return errors
    
    # Get operation table
    op_table = op_elem.find('opTable')
    if op_table is None:
        errors.append(f"Missing <opTable> element for operation '{op_name}'")
        return errors
    
    int_array = op_table.find('intArray')
    if int_array is None:
        errors.append(f"Missing <intArray> element for operation '{op_name}'")
        return errors
    
    # Parse and validate rows
    rows = list(int_array.findall('row'))
    
    # Check row count - use 1 if arity <= 1 else cardinality^(arity-1)
    expected_row_count = 1 if arity <= 1 else (cardinality ** (arity - 1))
    if len(rows) != expected_row_count:
        errors.append(f"Operation '{op_name}' has wrong number of rows: expected {expected_row_count}, got {len(rows)}")
        return errors
    
    # Check each row
    for i, row_elem in enumerate(rows):
        row_text = row_elem.text or ""
        row_values = _parse_row_values_safe(row_text, cardinality, op_name, file_path)
        
        if row_values is None:
            # Add error message for parsing failure
            errors.append(f"Operation '{op_name}' row {i} contains invalid values")
            continue
        
        # For unary operations, expect cardinality values in the single row
        if arity == 0:
            expected_row_size = 1
        elif arity == 1:
            expected_row_size = cardinality
        else:
            expected_row_size = cardinality ** (arity - 1)
        
        if len(row_values) != expected_row_size:
            errors.append(f"Operation '{op_name}' row {i} has wrong size: expected {expected_row_size}, got {len(row_values)}")
    
    return errors

def _parse_row_values_safe(row_text: str, cardinality: int, op_name: str, file_path: str) -> Optional[List[int]]:
    """Parse comma-separated values from a row, returning None on error (for validation mode)."""
    try:
        # Split by comma and convert to integers
        values = []
        for value_str in row_text.split(','):
            value_str = value_str.strip()
            if not value_str:
                continue
            
            try:
                value = int(value_str)
            except ValueError:
                # Don't raise, just return None to indicate error
                return None
            
            if value < 0 or value >= cardinality:
                # Don't raise, just return None to indicate error
                return None
            
            values.append(value)
        
        return values
        
    except Exception:
        # Don't raise, just return None to indicate error
        return None

def convert_format(input_file: Union[str, Path], output_file: Union[str, Path], 
                  target_format: str = "ua") -> None:
    """
    Convert algebra files between different formats.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        target_format: Target format ("ua", "json", etc.)
        
    Raises:
        NotImplementedError: This function is planned but not yet implemented
    """
    raise NotImplementedError("convert_format() is planned but not yet implemented")

def repair_ua_file(file_path: Union[str, Path], backup: bool = True) -> Tuple[bool, List[str]]:
    """
    Attempt to repair a malformed .ua file.
    
    Args:
        file_path: Path to the .ua file to repair
        backup: Whether to create a backup before attempting repair
        
    Returns:
        Tuple of (success, list_of_errors)
        
    Raises:
        NotImplementedError: This function is planned but not yet implemented
    """
    raise NotImplementedError("repair_ua_file() is planned but not yet implemented")

def list_ua_files(directory: Union[str, Path], recursive: bool = False, pattern: str = '*.ua') -> List[Path]:
    """
    List all .ua files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively in subdirectories
        pattern: File pattern to match (default: '*.ua')
        
    Returns:
        List of .ua file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))

def get_algebra_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get basic information about an algebra without full parsing.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Dictionary with algebra information
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        root = ET.fromstring(content)
        
        info = {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'valid': False,
            'errors': []
        }
        
        # Try to extract basic information
        basic_algebra = root.find('basicAlgebra')
        if basic_algebra is not None:
            alg_name_elem = basic_algebra.find('algName')
            if alg_name_elem is not None:
                info['name'] = alg_name_elem.text or "unnamed"
            
            cardinality_elem = basic_algebra.find('cardinality')
            if cardinality_elem is not None:
                try:
                    info['cardinality'] = int(cardinality_elem.text)
                except (ValueError, TypeError):
                    info['errors'].append(f"Invalid cardinality: {cardinality_elem.text}")
            
            operations_elem = basic_algebra.find('operations')
            if operations_elem is not None:
                info['operation_count'] = len(operations_elem.findall('op'))
        
        # Validate file
        is_valid, errors = validate_ua_file(file_path)
        info['valid'] = is_valid
        info['errors'].extend(errors)
        
        return info
        
    except Exception as e:
        return {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'valid': False,
            'errors': [f"Error reading file: {e}"]
        }

