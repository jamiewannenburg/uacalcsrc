use uacalc::io::ExtFileFilter;
use uacalc::io::{ALG_EXT, XML_EXT, UAC_EXT, UA_EXT, CSV_EXT, TXT_EXT, UA_EXTS, ALL_ALG_EXTS, MACE4_EXTS};
use std::path::Path;
use crate::common::*;
use serde_json::json;

#[test]
fn test_new() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["new", "--description", "UA Files", "--exts", "ua,xml"],
        || {
            let _filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            json!({
                "command": "new",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "status": "ExtFileFilter created successfully"
            })
        }
    );
}

#[test]
fn test_new_single() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["new_single", "--description", "UA Files", "--ext", "ua"],
        || {
            let _filter = ExtFileFilter::new_single("UA Files", "ua");
            json!({
                "command": "new_single",
                "description": "UA Files",
                "ext": "ua",
                "status": "ExtFileFilter created successfully"
            })
        }
    );
}

#[test]
fn test_accept() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["accept", "--description", "UA Files", "--exts", "ua,xml", "--path", "example.ua"],
        || {
            let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            let path = Path::new("example.ua");
            let accepted = filter.accept(path);
            json!({
                "command": "accept",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "path": "example.ua",
                "status": accepted
            })
        }
    );
}

#[test]
fn test_accept_rejected() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["accept", "--description", "UA Files", "--exts", "ua,xml", "--path", "example.txt"],
        || {
            let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            let path = Path::new("example.txt");
            let accepted = filter.accept(path);
            json!({
                "command": "accept",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "path": "example.txt",
                "status": accepted
            })
        }
    );
}

#[test]
fn test_accept_directory() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["accept", "--description", "UA Files", "--exts", "ua,xml", "--path", "/tmp"],
        || {
            let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            let path = Path::new("/tmp");
            let accepted = filter.accept(path);
            json!({
                "command": "accept",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "path": "/tmp",
                "status": accepted
            })
        }
    );
}

#[test]
fn test_get_description() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["get_description", "--description", "UA Files", "--exts", "ua,xml"],
        || {
            let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            let description = filter.get_description();
            json!({
                "command": "get_description",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "status": description
            })
        }
    );
}

#[test]
fn test_get_extensions() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["get_extensions", "--description", "UA Files", "--exts", "ua,xml"],
        || {
            let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
            let extensions: Vec<String> = filter.get_extensions().iter().cloned().collect();
            json!({
                "command": "get_extensions",
                "description": "UA Files",
                "exts": ["ua", "xml"],
                "status": extensions
            })
        }
    );
}

#[test]
fn test_split_off_extension() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["split_off_extension", "--path", "example.ua"],
        || {
            let path = Path::new("example.ua");
            let (name, ext) = ExtFileFilter::split_off_extension(path);
            json!({
                "command": "split_off_extension",
                "path": "example.ua",
                "status": {
                    "name": name,
                    "extension": ext
                }
            })
        }
    );
}

#[test]
fn test_split_off_extension_no_ext() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["split_off_extension", "--path", "noextension"],
        || {
            let path = Path::new("noextension");
            let (name, ext) = ExtFileFilter::split_off_extension(path);
            json!({
                "command": "split_off_extension",
                "path": "noextension",
                "status": {
                    "name": name,
                    "extension": ext
                }
            })
        }
    );
}

#[test]
fn test_get_extension() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["get_extension", "--path", "example.ua"],
        || {
            let path = Path::new("example.ua");
            let ext = ExtFileFilter::get_extension(path);
            json!({
                "command": "get_extension",
                "path": "example.ua",
                "status": ext
            })
        }
    );
}

#[test]
fn test_get_extension_no_ext() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.io.ExtFileFilterWrapper",
        ["get_extension", "--path", "noextension"],
        || {
            let path = Path::new("noextension");
            let ext = ExtFileFilter::get_extension(path);
            json!({
                "command": "get_extension",
                "path": "noextension",
                "status": ext
            })
        }
    );
}

#[test]
fn test_constants() {
    // Test that constants match Java implementation
    assert_eq!(ALG_EXT, "alg");
    assert_eq!(XML_EXT, "xml");
    assert_eq!(UAC_EXT, "uac");
    assert_eq!(UA_EXT, "ua");
    assert_eq!(CSV_EXT, "csv");
    assert_eq!(TXT_EXT, "txt");
}

#[test]
fn test_static_lists() {
    // Test that static lists match Java implementation
    let ua_exts = &*UA_EXTS;
    assert_eq!(ua_exts.len(), 2);
    assert!(ua_exts.contains(&"ua".to_string()));
    assert!(ua_exts.contains(&"xml".to_string()));
    
    let all_alg_exts = &*ALL_ALG_EXTS;
    assert_eq!(all_alg_exts.len(), 3);
    assert!(all_alg_exts.contains(&"ua".to_string()));
    assert!(all_alg_exts.contains(&"xml".to_string()));
    assert!(all_alg_exts.contains(&"alg".to_string()));
    
    let mace4_exts = &*MACE4_EXTS;
    assert_eq!(mace4_exts.len(), 1);
    assert!(mace4_exts.contains(&"m4".to_string()));
}

#[test]
fn test_new_safe_validation() {
    // Test validation in new_safe method
    let result = ExtFileFilter::new_safe("", vec!["ua".to_string()]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Description cannot be empty");
    
    let result = ExtFileFilter::new_safe("UA Files", vec![]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Extensions list cannot be empty");
    
    let result = ExtFileFilter::new_safe("UA Files", vec!["ua".to_string()]);
    assert!(result.is_ok());
}

#[test]
fn test_new_single_safe_validation() {
    // Test validation in new_single_safe method
    let result = ExtFileFilter::new_single_safe("", "ua");
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Description cannot be empty");
    
    let result = ExtFileFilter::new_single_safe("UA Files", "");
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Extension cannot be empty");
    
    let result = ExtFileFilter::new_single_safe("UA Files", "ua");
    assert!(result.is_ok());
}

#[test]
fn test_display() {
    let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    let display_str = format!("{}", filter);
    assert_eq!(display_str, "ExtFileFilter(UA Files)");
}

#[test]
fn test_equality() {
    let filter1 = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    let filter2 = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    let filter3 = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    
    assert_eq!(filter1, filter2);
    assert_ne!(filter1, filter3);
}

#[test]
fn test_hash() {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let filter1 = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    let filter2 = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    let filter3 = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    let mut hasher3 = DefaultHasher::new();
    
    filter1.hash(&mut hasher1);
    filter2.hash(&mut hasher2);
    filter3.hash(&mut hasher3);
    
    assert_eq!(hasher1.finish(), hasher2.finish());
    assert_ne!(hasher1.finish(), hasher3.finish());
}
