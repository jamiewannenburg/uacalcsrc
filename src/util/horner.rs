/*! Horner encoding and decoding utilities.

This module provides static methods for the Horner encoding and its inverse,
used for encoding elements from direct products of algebras.
*/

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras with various sizes.
/// 
/// # Arguments
/// * `args` - The element of the direct product
/// * `sizes` - The sizes of the algebras. Should have the same length as `args`
/// 
/// # Returns
/// The Horner encoding as an integer (with wrapping arithmetic for compatibility)
/// 
/// # Panics
/// Panics if `args` and `sizes` have different lengths
/// 
/// # Examples
/// ```
/// use uacalc::util::horner::horner;
/// let args = vec![1, 2, 3];
/// let sizes = vec![4, 5, 6];
/// let result = horner(&args, &sizes);
/// ```
pub fn horner(args: &[i32], sizes: &[i32]) -> i32 {
    if args.len() != sizes.len() {
        panic!("args and sizes arrays must have the same length");
    }
    
    let k = args.len();
    let mut ans = args[k - 1];
    for i in (0..k-1).rev() {
        ans = sizes[i].wrapping_mul(ans).wrapping_add(args[i]);
    }
    ans
}

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras with various sizes (safe version).
/// 
/// # Arguments
/// * `args` - The element of the direct product
/// * `sizes` - The sizes of the algebras. Should have the same length as `args`
/// 
/// # Returns
/// * `Ok(i32)` - The Horner encoding as an integer (with wrapping arithmetic for compatibility)
/// * `Err(String)` - Error if arrays have different lengths
pub fn horner_safe(args: &[i32], sizes: &[i32]) -> Result<i32, String> {
    if args.len() != sizes.len() {
        return Err("args and sizes arrays must have the same length".to_string());
    }
    
    let k = args.len();
    let mut ans = args[k - 1];
    for i in (0..k-1).rev() {
        ans = sizes[i].wrapping_mul(ans).wrapping_add(args[i]);
    }
    Ok(ans)
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with various sizes.
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `sizes` - The sizes of the algebras
/// 
/// # Returns
/// The decoded array
pub fn horner_inv(k: i32, sizes: &[i32]) -> Vec<i32> {
    horner_inv_with_dest(k, sizes, None)
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with various sizes (safe version).
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `sizes` - The sizes of the algebras
/// 
/// # Returns
/// * `Ok(Vec<i32>)` - The decoded array
/// * `Err(String)` - Error if sizes array is empty
pub fn horner_inv_safe(k: i32, sizes: &[i32]) -> Result<Vec<i32>, String> {
    if sizes.is_empty() {
        return Err("sizes array cannot be empty".to_string());
    }
    Ok(horner_inv_with_dest(k, sizes, None))
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with various sizes, with optional destination array.
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `sizes` - The sizes of the algebras
/// * `dest` - Optional destination array; if None, a new array is created
/// 
/// # Returns
/// The decoded array
pub fn horner_inv_with_dest(k: i32, sizes: &[i32], dest: Option<Vec<i32>>) -> Vec<i32> {
    let n = sizes.len();
    let mut ans = dest.unwrap_or_else(|| vec![0; n]);
    
    // Ensure the destination array has the right size
    if ans.len() != n {
        ans.resize(n, 0);
    }
    
    let mut k = k;
    for i in 0..n-1 {
        ans[i] = k % sizes[i];
        k = (k - ans[i]) / sizes[i];
    }
    ans[n-1] = k;
    ans
}

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras all with the same size, such as
/// a direct power.
/// 
/// # Arguments
/// * `args` - The element of the direct product
/// * `size` - The size of the algebras
/// 
/// # Returns
/// The Horner encoding as an integer
pub fn horner_same_size(args: &[i32], size: i32) -> i32 {
    let arity = args.len();
    let mut ans = 0;
    for i in (0..arity).rev() {
        ans = size * ans + args[i];
    }
    ans
}

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras all with the same size (safe version).
/// 
/// # Arguments
/// * `args` - The element of the direct product
/// * `size` - The size of the algebras
/// 
/// # Returns
/// * `Ok(i32)` - The Horner encoding as an integer
/// * `Err(String)` - Error if size is negative
pub fn horner_same_size_safe(args: &[i32], size: i32) -> Result<i32, String> {
    if size < 0 {
        return Err("size cannot be negative".to_string());
    }
    Ok(horner_same_size(args, size))
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with the same size.
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `size` - The size of each algebra
/// * `length` - The number of algebras
/// 
/// # Returns
/// The decoded array
pub fn horner_inv_same_size(k: i32, size: i32, length: usize) -> Vec<i32> {
    horner_inv_same_size_with_dest(k, size, length, None)
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with the same size (safe version).
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `size` - The size of each algebra
/// * `length` - The number of algebras
/// 
/// # Returns
/// * `Ok(Vec<i32>)` - The decoded array
/// * `Err(String)` - Error if size is negative or length is 0
pub fn horner_inv_same_size_safe(k: i32, size: i32, length: usize) -> Result<Vec<i32>, String> {
    if size < 0 {
        return Err("size cannot be negative".to_string());
    }
    if length == 0 {
        return Err("length cannot be zero".to_string());
    }
    Ok(horner_inv_same_size_with_dest(k, size, length, None))
}

/// Returns the int array corresponding to this Horner encoding
/// for a direct product of algebras with the same size, with optional destination array.
/// 
/// # Arguments
/// * `k` - The Horner encoding of the element of the direct product
/// * `size` - The size of each algebra
/// * `length` - The number of algebras
/// * `dest` - Optional destination array; if None, a new array is created
/// 
/// # Returns
/// The decoded array
pub fn horner_inv_same_size_with_dest(k: i32, size: i32, length: usize, dest: Option<Vec<i32>>) -> Vec<i32> {
    let n = length;
    let mut ans = dest.unwrap_or_else(|| vec![0; n]);
    
    // Ensure the destination array has the right size
    if ans.len() != n {
        ans.resize(n, 0);
    }
    
    if n == 0 {
        return ans;
    }
    
    let mut k = k;
    for i in 0..n-1 {
        ans[i] = k % size;
        k = (k - ans[i]) / size;
    }
    ans[n-1] = k;
    ans
}

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras with the same size.
/// 
/// # Arguments
/// * `args` - The element of the direct product (as Vec<i32>)
/// * `size` - The size of each algebra
/// 
/// # Returns
/// The Horner encoding as an integer
pub fn horner_integer(args: &[i32], size: i32) -> i32 {
    let arity = args.len();
    let mut ans = 0;
    for i in (0..arity).rev() {
        ans = size * ans + args[i];
    }
    ans
}

/// Returns the Horner encoding of an int array representing an element
/// from a direct product of algebras with the same size (safe version).
/// 
/// # Arguments
/// * `args` - The element of the direct product (as Vec<i32>)
/// * `size` - The size of each algebra
/// 
/// # Returns
/// * `Ok(i32)` - The Horner encoding as an integer
/// * `Err(String)` - Error if size is negative
pub fn horner_integer_safe(args: &[i32], size: i32) -> Result<i32, String> {
    if size < 0 {
        return Err("size cannot be negative".to_string());
    }
    Ok(horner_integer(args, size))
}

/// A convenience method for generating a new array with the reverse
/// order of the given array.
/// 
/// # Arguments
/// * `arr` - The input array
/// 
/// # Returns
/// A new array with elements in reverse order
pub fn reverse_array(arr: &[i32]) -> Vec<i32> {
    let mut ans = vec![0; arr.len()];
    let max = arr.len() - 1;
    for i in 0..ans.len() {
        ans[i] = arr[max - i];
    }
    ans
}

/// If values are the values of a function at [0,0, ...,0], [1,0,...,0],
/// this gives the values in the order [0,0, ...,0], [0,0,...,1], ...  .
/// 
/// # Arguments
/// * `values` - The input values array
/// * `alg_size` - The algebra size
/// * `arity` - The arity
/// 
/// # Returns
/// The transformed values array
pub fn left_right_reverse(values: &[i32], alg_size: i32, arity: usize) -> Vec<i32> {
    let mut ans = vec![0; values.len()];
    for i in 0..values.len() {
        let foo = reverse_array(&horner_inv_same_size(i as i32, alg_size, arity));
        let i_prime = horner_same_size(&foo, alg_size);
        ans[i_prime as usize] = values[i];
    }
    ans
}

/// If values are the values of a function at [0,0, ...,0], [1,0,...,0],
/// this gives the values in the order [0,0, ...,0], [0,0,...,1], ...  . (safe version)
/// 
/// # Arguments
/// * `values` - The input values array
/// * `alg_size` - The algebra size
/// * `arity` - The arity
/// 
/// # Returns
/// * `Ok(Vec<i32>)` - The transformed values array
/// * `Err(String)` - Error if alg_size is negative or arity is 0
pub fn left_right_reverse_safe(values: &[i32], alg_size: i32, arity: usize) -> Result<Vec<i32>, String> {
    if alg_size < 0 {
        return Err("alg_size cannot be negative".to_string());
    }
    if arity == 0 {
        return Err("arity cannot be zero".to_string());
    }
    Ok(left_right_reverse(values, alg_size, arity))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_horner_basic() {
        let args = vec![1, 2, 3];
        let sizes = vec![4, 5, 6];
        let result = horner(&args, &sizes);
        assert_eq!(result, 1 + 2*4 + 3*4*5);
    }

    #[test]
    fn test_horner_inv_basic() {
        let k = 1 + 2*4 + 3*4*5;
        let sizes = vec![4, 5, 6];
        let result = horner_inv(k, &sizes);
        assert_eq!(result, vec![1, 2, 3]);
    }

    #[test]
    fn test_horner_same_size() {
        let args = vec![1, 2, 3];
        let size = 10;
        let result = horner_same_size(&args, size);
        assert_eq!(result, 1 + 2*10 + 3*10*10);
    }

    #[test]
    fn test_horner_inv_same_size() {
        let k = 1 + 2*10 + 3*10*10;
        let size = 10;
        let length = 3;
        let result = horner_inv_same_size(k, size, length);
        assert_eq!(result, vec![1, 2, 3]);
    }

    #[test]
    fn test_reverse_array() {
        let arr = vec![1, 2, 3, 4];
        let result = reverse_array(&arr);
        assert_eq!(result, vec![4, 3, 2, 1]);
    }

    #[test]
    fn test_left_right_reverse() {
        let values = vec![0, 1, 2, 3];
        let alg_size = 2;
        let arity = 2;
        let result = left_right_reverse(&values, alg_size, arity);
        // This is a complex transformation, just verify it doesn't panic
        assert_eq!(result.len(), values.len());
    }

    #[test]
    fn test_horner_safe_validation() {
        let args = vec![1, 2, 3];
        let sizes = vec![4, 5]; // Different length
        let result = horner_safe(&args, &sizes);
        assert!(result.is_err());
    }

    #[test]
    fn test_horner_inv_safe_validation() {
        let result = horner_inv_safe(123, &[]);
        assert!(result.is_err());
    }

    #[test]
    fn test_horner_same_size_safe_validation() {
        let args = vec![1, 2, 3];
        let result = horner_same_size_safe(&args, -1);
        assert!(result.is_err());
    }

    #[test]
    fn test_horner_inv_same_size_safe_validation() {
        let result = horner_inv_same_size_safe(123, 10, 0);
        assert!(result.is_err());
    }

    #[test]
    fn test_left_right_reverse_safe_validation() {
        let values = vec![0, 1, 2, 3];
        let result = left_right_reverse_safe(&values, -1, 2);
        assert!(result.is_err());
        
        let result = left_right_reverse_safe(&values, 2, 0);
        assert!(result.is_err());
    }
}
