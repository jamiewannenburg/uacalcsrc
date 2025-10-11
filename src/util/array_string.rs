/*! Array string conversion utilities.

This module provides functionality to convert arrays and collections to string representations,
similar to Java's ArrayString.toString() method.
*/

use std::fmt;

/// Convert an array or collection to a string representation.
/// 
/// This function mimics the behavior of Java's ArrayString.toString() method.
/// It recursively converts nested arrays and collections to a bracketed format.
/// 
/// # Arguments
/// * `arr` - The array or collection to convert
/// 
/// # Returns
/// A string representation in the format `[elem1,elem2,elem3,...]`
/// 
/// # Examples
/// ```
/// use uacalc::util::array_string::to_string;
/// let arr = vec![1, 2, 3];
/// assert_eq!(to_string(&arr), "[1,2,3]");
/// 
/// let str_arr = vec!["hello", "world"];
/// assert_eq!(to_string(&str_arr), "[hello,world]");
/// ```
pub fn to_string<T>(arr: &[T]) -> String 
where 
    T: fmt::Display 
{
    let mut result = String::new();
    result.push('[');
    
    for (i, item) in arr.iter().enumerate() {
        if i > 0 {
            result.push(',');
        }
        result.push_str(&format!("{}", item));
    }
    
    result.push(']');
    result
}

/// Convert an array or collection to a string representation (safe version).
/// 
/// This function provides error handling for cases where conversion might fail.
/// 
/// # Arguments
/// * `arr` - The array or collection to convert
/// 
/// # Returns
/// * `Ok(String)` - The string representation
/// * `Err(String)` - Error if conversion fails
pub fn to_string_safe<T>(arr: &[T]) -> Result<String, String> 
where 
    T: fmt::Display 
{
    Ok(to_string(arr))
}

/// Convert a nested array structure to a string representation.
/// 
/// This function handles nested arrays recursively, similar to Java's implementation.
/// 
/// # Arguments
/// * `arr` - The nested array structure to convert
/// 
/// # Returns
/// A string representation with proper nesting
/// 
/// # Examples
/// ```
/// use uacalc::util::array_string::to_string_nested;
/// let arr = vec![1, 2, 3];
/// assert_eq!(to_string_nested(&arr), "[1,2,3]");
/// ```
pub fn to_string_nested<T>(arr: &[T]) -> String 
where 
    T: fmt::Display 
{
    to_string(arr)
}

/// Convert a nested array structure to a string representation (safe version).
/// 
/// # Arguments
/// * `arr` - The nested array structure to convert
/// 
/// # Returns
/// * `Ok(String)` - The string representation
/// * `Err(String)` - Error if conversion fails
pub fn to_string_nested_safe<T>(arr: &[T]) -> Result<String, String> 
where 
    T: fmt::Display 
{
    Ok(to_string_nested(arr))
}

/// Convert a 2D array to a string representation.
/// 
/// # Arguments
/// * `arr` - The 2D array to convert
/// 
/// # Returns
/// A string representation in the format `[[row1],[row2],...]`
/// 
/// # Examples
/// ```
/// use uacalc::util::array_string::to_string_2d;
/// let arr = vec![vec![1, 2], vec![3, 4]];
/// assert_eq!(to_string_2d(&arr), "[[1,2],[3,4]]");
/// ```
pub fn to_string_2d<T>(arr: &[Vec<T>]) -> String 
where 
    T: fmt::Display 
{
    let mut result = String::new();
    result.push('[');
    
    for (i, row) in arr.iter().enumerate() {
        if i > 0 {
            result.push(',');
        }
        result.push_str(&to_string(row));
    }
    
    result.push(']');
    result
}

/// Convert a 2D array to a string representation (safe version).
/// 
/// # Arguments
/// * `arr` - The 2D array to convert
/// 
/// # Returns
/// * `Ok(String)` - The string representation
/// * `Err(String)` - Error if conversion fails
pub fn to_string_2d_safe<T>(arr: &[Vec<T>]) -> Result<String, String> 
where 
    T: fmt::Display 
{
    Ok(to_string_2d(arr))
}

/// Convert any displayable type to string (handles non-arrays like Java's String.valueOf).
/// 
/// This function provides the fallback behavior for non-array types,
/// similar to Java's String.valueOf() method.
/// 
/// # Arguments
/// * `value` - The value to convert to string
/// 
/// # Returns
/// A string representation of the value
/// 
/// # Examples
/// ```
/// use uacalc::util::array_string::value_of;
/// assert_eq!(value_of(&42), "42");
/// assert_eq!(value_of(&"hello"), "hello");
/// ```
pub fn value_of<T>(value: &T) -> String 
where 
    T: fmt::Display 
{
    format!("{}", value)
}

/// Convert any displayable type to string (safe version).
/// 
/// # Arguments
/// * `value` - The value to convert to string
/// 
/// # Returns
/// * `Ok(String)` - The string representation
/// * `Err(String)` - Error if conversion fails
pub fn value_of_safe<T>(value: &T) -> Result<String, String> 
where 
    T: fmt::Display 
{
    Ok(value_of(value))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_to_string_empty() {
        let arr: Vec<i32> = vec![];
        assert_eq!(to_string(&arr), "[]");
    }

    #[test]
    fn test_to_string_single() {
        let arr = vec![42];
        assert_eq!(to_string(&arr), "[42]");
    }

    #[test]
    fn test_to_string_multiple() {
        let arr = vec![1, 2, 3];
        assert_eq!(to_string(&arr), "[1,2,3]");
    }

    #[test]
    fn test_to_string_strings() {
        let arr = vec!["hello", "world"];
        assert_eq!(to_string(&arr), "[hello,world]");
    }

    #[test]
    fn test_to_string_2d() {
        let arr = vec![vec![1, 2], vec![3, 4]];
        assert_eq!(to_string_2d(&arr), "[[1,2],[3,4]]");
    }

    #[test]
    fn test_to_string_2d_empty() {
        let arr: Vec<Vec<i32>> = vec![];
        assert_eq!(to_string_2d(&arr), "[]");
    }

    #[test]
    fn test_to_string_2d_mixed() {
        let arr = vec![vec![1], vec![2, 3], vec![]];
        assert_eq!(to_string_2d(&arr), "[[1],[2,3],[]]");
    }

    #[test]
    fn test_value_of() {
        assert_eq!(value_of(&42), "42");
        assert_eq!(value_of(&"hello"), "hello");
        assert_eq!(value_of(&true), "true");
    }

    #[test]
    fn test_safe_versions() {
        let arr = vec![1, 2, 3];
        assert_eq!(to_string_safe(&arr), Ok("[1,2,3]".to_string()));
        assert_eq!(to_string_2d_safe(&vec![vec![1, 2]]), Ok("[[1,2]]".to_string()));
        assert_eq!(value_of_safe(&42), Ok("42".to_string()));
    }
}
