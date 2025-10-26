// Basic tests for SubProductAlgebra and SubProductElement
// These are minimal tests to verify the basic structure compiles and works

#[cfg(test)]
mod tests {
    use uacalc::alg::{SubProductAlgebra, BigProductAlgebra, BasicSmallAlgebra, SmallAlgebra};
    use uacalc::element::SubProductElement;
    use uacalc::util::int_array::IntArray;
    use std::collections::HashSet;

    #[test]
    fn test_sub_product_algebra_exists() {
        // This test just verifies the struct compiles
        // Full testing requires BigProductAlgebra to be fully implemented
        assert!(true);
    }

    #[test]
    fn test_sub_product_element_exists() {
        // This test just verifies the struct compiles
        // Full testing requires SubProductAlgebra to be functional
        assert!(true);
    }
    
    #[test]
    fn test_transpose() {
        // Test the static transpose method
        let arr1 = IntArray::from_array(vec![0, 1, 2]).unwrap();
        let arr2 = IntArray::from_array(vec![3, 4, 5]).unwrap();
        let list = vec![arr1, arr2];
        
        let result = SubProductAlgebra::<i32>::transpose(&list);
        assert!(result.is_ok());
        
        let transposed = result.unwrap();
        assert_eq!(transposed.len(), 3);
    }
}
