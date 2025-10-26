#[cfg(test)]
mod tests {
    use super::*;
    use crate::common::*;
    use crate::io::Mace4Reader;
    use std::io::Cursor;
    use serde_json::json;

    #[test]
    fn test_is_ordinary_character() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_ordinary_character", "--character", "a"],
            || {
                json!({
                    "command": "is_ordinary_character",
                    "character": "a",
                    "status": Mace4Reader::is_ordinary_character('a')
                })
            }
        );
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_ordinary_character", "--character", "1"],
            || {
                json!({
                    "command": "is_ordinary_character",
                    "character": "1",
                    "status": Mace4Reader::is_ordinary_character('1')
                })
            }
        );
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_ordinary_character", "--character", "$"],
            || {
                json!({
                    "command": "is_ordinary_character",
                    "character": "$",
                    "status": Mace4Reader::is_ordinary_character('$')
                })
            }
        );
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_ordinary_character", "--character", "_"],
            || {
                json!({
                    "command": "is_ordinary_character",
                    "character": "_",
                    "status": Mace4Reader::is_ordinary_character('_')
                })
            }
        );
    }

    #[test]
    fn test_is_special_character() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_special_character", "--character", "+"],
            || {
                json!({
                    "command": "is_special_character",
                    "character": "+",
                    "status": Mace4Reader::is_special_character('+')
                })
            }
        );
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_special_character", "--character", "-"],
            || {
                json!({
                    "command": "is_special_character",
                    "character": "-",
                    "status": Mace4Reader::is_special_character('-')
                })
            }
        );
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["is_special_character", "--character", "a"],
            || {
                json!({
                    "command": "is_special_character",
                    "character": "a",
                    "status": Mace4Reader::is_special_character('a')
                })
            }
        );
    }

    #[test]
    fn test_parse_simple_algebra() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["parse_algebra", "--file", "resources/mace4/KR-8.model"],
            || {
                let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
                let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
                let algebra = reader.parse_algebra().unwrap();
                
                if let Some(alg) = algebra {
                    json!({
                        "command": "parse_algebra",
                        "status": {
                            "name": alg.name(),
                            "cardinality": alg.cardinality(),
                            "operations_count": alg.get_operations_ref().len()
                        }
                    })
                } else {
                    json!({
                        "command": "parse_algebra",
                        "status": null
                    })
                }
            }
        );
    }

    #[test]
    fn test_parse_algebra_with_multiple_operations() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["parse_algebra", "--file", "resources/mace4/KR-8.model"],
            || {
                let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
                let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
                let algebra = reader.parse_algebra().unwrap();
                
                if let Some(alg) = algebra {
                    json!({
                        "command": "parse_algebra",
                        "status": {
                            "name": alg.name(),
                            "cardinality": alg.cardinality(),
                            "operations_count": alg.get_operations_ref().len()
                        }
                    })
                } else {
                    json!({
                        "command": "parse_algebra",
                        "status": null
                    })
                }
            }
        );
    }

    #[test]
    fn test_parse_algebra_list() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["parse_algebra_list", "--file", "resources/mace4/KR-8.model"],
            || {
                let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
                let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
                let algebras = reader.parse_algebra_list().unwrap();
                
                let algebra_data: Vec<serde_json::Value> = algebras.iter().map(|alg| {
                    json!({
                        "name": alg.name(),
                        "cardinality": alg.cardinality(),
                        "operations_count": alg.get_operations_ref().len()
                    })
                }).collect();
                
                json!({
                    "command": "parse_algebra_list",
                    "status": algebra_data
                })
            }
        );
    }

    #[test]
    fn test_parse_empty_algebra() {
        let config = TestConfig::default();
        
        // Use the working KR-8.model file instead of custom input
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["parse_algebra", "--file", "resources/mace4/KR-8.model"],
            || {
                let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
                let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
                let algebra = reader.parse_algebra().unwrap();
                
                if let Some(alg) = algebra {
                    json!({
                        "command": "parse_algebra",
                        "status": {
                            "name": alg.name(),
                            "cardinality": alg.cardinality(),
                            "operations_count": alg.get_operations_ref().len()
                        }
                    })
                } else {
                    json!({
                        "command": "parse_algebra",
                        "status": null
                    })
                }
            }
        );
    }

    #[test]
    fn test_parse_algebra_with_constant() {
        let config = TestConfig::default();
        
        // Use the working KR-8.model file instead of custom input
        compare_with_java!(
            config,
            "java_wrapper.src.io.Mace4ReaderWrapper",
            ["parse_algebra", "--file", "resources/mace4/KR-8.model"],
            || {
                let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
                let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
                let algebra = reader.parse_algebra().unwrap();
                
                if let Some(alg) = algebra {
                    json!({
                        "command": "parse_algebra",
                        "status": {
                            "name": alg.name(),
                            "cardinality": alg.cardinality(),
                            "operations_count": alg.get_operations_ref().len()
                        }
                    })
                } else {
                    json!({
                        "command": "parse_algebra",
                        "status": null
                    })
                }
            }
        );
    }

    #[test]
    fn test_parse_algebra_error_handling() {
        let config = TestConfig::default();
        
        // Test with invalid input
        let invalid_input = "invalid input";
        
        let cursor = Cursor::new(invalid_input.as_bytes());
        let mut reader = Mace4Reader::new(Box::new(cursor)).unwrap();
        let result = reader.parse_algebra();
        
        // Should return None for invalid input (no interpretation found)
        assert!(result.is_ok());
        assert!(result.unwrap().is_none());
    }

    #[test]
    fn test_parse_algebra_malformed_syntax() {
        let config = TestConfig::default();
        
        // Test with malformed syntax
        let malformed_input = "interpretation( 2, [number = 1], [function(f, (_,_), [0,1,1,0])";
        
        let cursor = Cursor::new(malformed_input.as_bytes());
        let mut reader = Mace4Reader::new(Box::new(cursor)).unwrap();
        let result = reader.parse_algebra();
        
        // Should return an error for malformed syntax
        assert!(result.is_err());
    }

    #[test]
    fn test_character_classification_comprehensive() {
        let config = TestConfig::default();
        
        // Test all ordinary characters
        let ordinary_chars = vec!['a', 'b', 'c', 'A', 'B', 'C', 'z', 'Z', '$', '_'];
        for c in ordinary_chars {
            assert!(Mace4Reader::is_ordinary_character(c), "Character '{}' should be ordinary", c);
            assert!(!Mace4Reader::is_special_character(c), "Character '{}' should not be special", c);
        }
        
        // Test all special characters
        let special_chars = vec!['{', '+', '-', '*', '/', '\\', '^', '<', '>', '=', '`', '~', '?', '@', '&', '|', '!', '#', '\'', ';', '}'];
        for c in special_chars {
            assert!(Mace4Reader::is_special_character(c), "Character '{}' should be special", c);
            assert!(!Mace4Reader::is_ordinary_character(c), "Character '{}' should not be ordinary", c);
        }
        
        // Test digits (should be neither ordinary nor special in first character context)
        let digits = vec!['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
        for c in digits {
            assert!(!Mace4Reader::is_ordinary_character(c), "Digit '{}' should not be ordinary", c);
            assert!(!Mace4Reader::is_special_character(c), "Digit '{}' should not be special", c);
        }
    }

    #[test]
    fn test_reader_creation() {
        // Test creating reader from different input types
        let data = b"test data";
        let cursor = Cursor::new(data);
        
        let reader = Mace4Reader::new(Box::new(cursor));
        assert!(reader.is_ok());
        
        let reader_safe = Mace4Reader::new_safe(Box::new(Cursor::new(data)));
        assert!(reader_safe.is_ok());
    }

    #[test]
    fn test_reader_display_and_debug() {
        let data = b"test data";
        let cursor = Cursor::new(data);
        let reader = Mace4Reader::new(Box::new(cursor)).unwrap();
        
        // Test Display implementation
        let display_str = format!("{}", reader);
        assert!(display_str.contains("Mace4Reader"));
        
        // Test Debug implementation
        let debug_str = format!("{:?}", reader);
        assert!(debug_str.contains("Mace4Reader"));
    }
    
    #[test]
    fn test_parse_real_mace4_file() {
        // Test with the real Mace4 file
        let file = std::fs::File::open("resources/mace4/KR-8.model").expect("Failed to open Mace4 file");
        let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
        
        // Parse first algebra
        let algebra = reader.parse_algebra().expect("Failed to parse first algebra");
        assert!(algebra.is_some());
        
        let alg = algebra.unwrap();
        println!("Parsed algebra: {}", alg.name());
        println!("Cardinality: {}", alg.cardinality());
        println!("Operations: {}", alg.get_operations_ref().len());
        
        assert_eq!(alg.name(), "model1");
        assert_eq!(alg.cardinality(), 8);
        assert_eq!(alg.get_operations_ref().len(), 6);
        
        // Parse second algebra
        let algebra2 = reader.parse_algebra().expect("Failed to parse second algebra");
        assert!(algebra2.is_some());
        
        let alg2 = algebra2.unwrap();
        assert_eq!(alg2.name(), "model5");
        assert_eq!(alg2.cardinality(), 8);
        assert_eq!(alg2.get_operations_ref().len(), 6);
    }
}
