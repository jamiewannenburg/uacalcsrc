use uacalc::util::array_string;

/// Test basic array string conversion
#[test]
fn test_to_string_int() {
    let arr = vec![1, 2, 3];
    let result = array_string::to_string(&arr);
    assert_eq!(result, "[1,2,3]");
}

/// Test empty array string conversion
#[test]
fn test_to_string_empty() {
    let arr: Vec<i32> = vec![];
    let result = array_string::to_string(&arr);
    assert_eq!(result, "[]");
}

/// Test single element array string conversion
#[test]
fn test_to_string_single() {
    let arr = vec![42];
    let result = array_string::to_string(&arr);
    assert_eq!(result, "[42]");
}

/// Test 2D array string conversion
#[test]
fn test_to_string_2d_int() {
    let arr = vec![vec![1, 2], vec![3, 4]];
    let result = array_string::to_string_2d(&arr);
    assert_eq!(result, "[[1,2],[3,4]]");
}

/// Test 2D empty array string conversion
#[test]
fn test_to_string_2d_empty() {
    let arr: Vec<Vec<i32>> = vec![];
    let result = array_string::to_string_2d(&arr);
    assert_eq!(result, "[]");
}

/// Test 2D mixed array string conversion
#[test]
fn test_to_string_2d_mixed() {
    let arr = vec![vec![1], vec![2, 3], vec![]];
    let result = array_string::to_string_2d(&arr);
    assert_eq!(result, "[[1],[2,3],[]]");
}

/// Test string array conversion
#[test]
fn test_to_string_str() {
    let arr = vec!["hello".to_string(), "world".to_string()];
    let result = array_string::to_string(&arr);
    assert_eq!(result, "[hello,world]");
}

/// Test 2D string array conversion
#[test]
fn test_to_string_2d_str() {
    let arr = vec![vec!["a".to_string(), "b".to_string()], vec!["c".to_string(), "d".to_string()]];
    let result = array_string::to_string_2d(&arr);
    assert_eq!(result, "[[a,b],[c,d]]");
}

/// Test value_of function
#[test]
fn test_value_of() {
    let value = "hello";
    let result = array_string::value_of(&value);
    assert_eq!(result, "hello");
}

/// Test value_of with integer
#[test]
fn test_value_of_int() {
    let value = 42;
    let result = array_string::value_of(&value);
    assert_eq!(result, "42");
}

/// Test safe versions of functions
#[test]
fn test_safe_versions() {
    // Test to_string_safe
    let arr = vec![1, 2, 3];
    let result = array_string::to_string_safe(&arr).unwrap();
    assert_eq!(result, "[1,2,3]");
    
    // Test to_string_2d_safe
    let arr_2d = vec![vec![1, 2], vec![3, 4]];
    let result_2d = array_string::to_string_2d_safe(&arr_2d).unwrap();
    assert_eq!(result_2d, "[[1,2],[3,4]]");
    
    // Test value_of_safe
    let value = 42;
    let result_value = array_string::value_of_safe(&value).unwrap();
    assert_eq!(result_value, "42");
}

/// Test nested string conversion
#[test]
fn test_nested_conversion() {
    let arr = vec![vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 9]];
    let result = array_string::to_string_2d(&arr);
    assert_eq!(result, "[[1,2,3],[4,5,6],[7,8,9]]");
}

/// Test large array conversion
#[test]
fn test_large_array() {
    let arr = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let result = array_string::to_string(&arr);
    assert_eq!(result, "[1,2,3,4,5,6,7,8,9,10]");
}
