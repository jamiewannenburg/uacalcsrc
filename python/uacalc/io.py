"""
I/O module for UACalc algebra files.

This module provides functionality for reading and writing .ua files,
maintaining compatibility with the existing Java UACalc implementation.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
import logging

from . import Algebra, Operation, create_algebra, create_operation

logger = logging.getLogger(__name__)

class UACalcIOError(Exception):
    """Exception raised for UACalc I/O errors."""
    pass

def load_algebra(file_path: Union[str, Path]) -> Algebra:
    """
    Load an algebra from a .ua file.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Algebra object loaded from the file
        
    Raises:
        UACalcIOError: If the file cannot be parsed or is invalid
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise UACalcIOError(f"File not found: {file_path}")
    
    if file_path.suffix.lower() != '.ua':
        raise UACalcIOError(f"File must have .ua extension: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return _parse_ua_content(content, file_path.name)
        
    except Exception as e:
        raise UACalcIOError(f"Failed to load algebra from {file_path}: {e}") from e

def save_algebra(algebra: Algebra, file_path: Union[str, Path]) -> None:
    """
    Save an algebra to a .ua file.
    
    Args:
        algebra: Algebra object to save
        file_path: Path where to save the .ua file
        
    Raises:
        UACalcIOError: If the algebra cannot be saved
    """
    file_path = Path(file_path)
    
    try:
        content = _generate_ua_content(algebra)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        raise UACalcIOError(f"Failed to save algebra to {file_path}: {e}") from e

def _parse_ua_content(content: str, filename: str) -> Algebra:
    """Parse the content of a .ua file."""
    try:
        # Remove any BOM and normalize line endings
        content = content.replace('\ufeff', '').replace('\r\n', '\n')
        
        # Parse XML content
        root = ET.fromstring(content)
        
        # Extract basic information
        algebra_name = root.get('name', filename.replace('.ua', ''))
        size = int(root.get('size', '0'))
        
        if size <= 0:
            raise UACalcIOError("Invalid algebra size")
        
        # Create universe
        universe = list(range(size))
        
        # Create algebra
        algebra = create_algebra(algebra_name, universe)
        
        # Parse operations
        for op_elem in root.findall('.//op'):
            op_name = op_elem.get('name', '')
            op_arity = int(op_elem.get('arity', '0'))
            
            # Parse operation table
            table = _parse_operation_table(op_elem, op_arity, size)
            
            # Create operation
            operation = create_operation(op_name, op_arity, table)
            algebra.add_operation(op_name, operation)
        
        return algebra
        
    except ET.ParseError as e:
        raise UACalcIOError(f"Invalid XML in .ua file: {e}") from e
    except ValueError as e:
        raise UACalcIOError(f"Invalid value in .ua file: {e}") from e

def _parse_operation_table(op_elem: ET.Element, arity: int, size: int) -> List[List[int]]:
    """Parse operation table from XML element."""
    table = []
    
    # Handle different table formats
    table_elem = op_elem.find('table')
    if table_elem is not None:
        # Parse table content
        table_text = table_elem.text or ''
        table = _parse_table_text(table_text, arity, size)
    else:
        # Try to parse from individual entries
        table = _parse_table_entries(op_elem, arity, size)
    
    return table

def _parse_table_text(table_text: str, arity: int, size: int) -> List[List[int]]:
    """Parse table from text representation."""
    table = []
    
    # Split by lines and process each line
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
    
    for line in lines:
        # Split by whitespace and convert to integers
        values = [int(x) for x in line.split()]
        
        if len(values) != arity + 1:  # args + result
            raise UACalcIOError(f"Invalid table row length: expected {arity + 1}, got {len(values)}")
        
        table.append(values)
    
    return table

def _parse_table_entries(op_elem: ET.Element, arity: int, size: int) -> List[List[int]]:
    """Parse table from individual entry elements."""
    table = []
    
    for entry_elem in op_elem.findall('entry'):
        args_text = entry_elem.get('args', '')
        result = int(entry_elem.get('result', '0'))
        
        # Parse arguments
        args = [int(x) for x in args_text.split() if x.strip()]
        
        if len(args) != arity:
            raise UACalcIOError(f"Invalid entry arguments: expected {arity}, got {len(args)}")
        
        # Combine args and result
        row = args + [result]
        table.append(row)
    
    return table

def _generate_ua_content(algebra: Algebra) -> str:
    """Generate .ua file content from algebra."""
    # Create XML structure
    root = ET.Element('algebra')
    root.set('name', algebra.name)
    root.set('size', str(algebra.cardinality()))
    
    # Add operations
    for i, operation in enumerate(algebra.operations()):
        op_elem = ET.SubElement(root, 'op')
        op_elem.set('name', operation.symbol)
        op_elem.set('arity', str(operation.arity))
        
        # Generate operation table
        table_elem = ET.SubElement(op_elem, 'table')
        table_text = _generate_table_text(operation, algebra.universe)
        table_elem.text = table_text
    
    # Convert to string with proper formatting
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding='unicode')

def _generate_table_text(operation: Operation, universe: List[int]) -> str:
    """Generate table text for an operation."""
    lines = []
    
    # Generate all possible input combinations
    for args in _generate_combinations(universe, operation.arity):
        result = operation.value(args)
        line = ' '.join(map(str, args)) + ' ' + str(result)
        lines.append(line)
    
    return '\n'.join(lines)

def _generate_combinations(elements: List[int], length: int) -> List[List[int]]:
    """Generate all combinations of elements with given length."""
    if length == 0:
        return [[]]
    
    if length == 1:
        return [[x] for x in elements]
    
    result = []
    for i, elem in enumerate(elements):
        for combo in _generate_combinations(elements, length - 1):
            result.append([elem] + combo)
    
    return result

def list_ua_files(directory: Union[str, Path]) -> List[Path]:
    """
    List all .ua files in a directory.
    
    Args:
        directory: Directory to search
        
    Returns:
        List of .ua file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    return list(directory.glob("*.ua"))

def validate_ua_file(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate a .ua file without loading it.
    
    Args:
        file_path: Path to the .ua file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic XML validation
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            errors.append(f"XML parsing error: {e}")
            return False, errors
        
        # Check required attributes
        if not root.get('size'):
            errors.append("Missing 'size' attribute")
        
        # Check operations
        for op_elem in root.findall('.//op'):
            if not op_elem.get('name'):
                errors.append("Operation missing 'name' attribute")
            if not op_elem.get('arity'):
                errors.append("Operation missing 'arity' attribute")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"File reading error: {e}")
        return False, errors

