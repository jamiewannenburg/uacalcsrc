pub struct AlgebraIO {
    // TODO: Implement algebra IO
}

pub struct AlgebraReader {
    // TODO: Implement algebra reader
}

pub struct AlgebraWriter {
    // TODO: Implement algebra writer
}

/// Exception thrown when an algebra file cannot be read or parsed correctly.
/// 
/// This exception is thrown when there are issues with the format, structure,
/// or content of an algebra file that prevent it from being processed.
/// 
/// # Examples
/// ```
/// use uacalc::io::BadAlgebraFileException;
/// 
/// let exception = BadAlgebraFileException::new("Invalid file format");
/// assert_eq!(exception.message(), "Invalid file format");
/// ```
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BadAlgebraFileException {
    message: String,
}

impl BadAlgebraFileException {
    /// Creates a new `BadAlgebraFileException` with the given message.
    /// 
    /// # Arguments
    /// * `message` - The error message describing what went wrong
    /// 
    /// # Returns
    /// A new `BadAlgebraFileException` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new("File not found");
    /// ```
    pub fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
        }
    }
    
    /// Creates a new `BadAlgebraFileException` with the given message (safe version).
    /// 
    /// This is the same as `new()` but provided for consistency with the pattern
    /// of having both `_safe` and regular versions of methods.
    /// 
    /// # Arguments
    /// * `message` - The error message describing what went wrong
    /// 
    /// # Returns
    /// `Ok(BadAlgebraFileException)` - A new exception instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new_safe("File corrupted").unwrap();
    /// ```
    pub fn new_safe(message: &str) -> Result<Self, String> {
        Ok(Self::new(message))
    }
    
    /// Returns the error message associated with this exception.
    /// 
    /// # Returns
    /// A reference to the error message string
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new("Invalid format");
    /// assert_eq!(exception.message(), "Invalid format");
    /// ```
    pub fn message(&self) -> &str {
        &self.message
    }
}

impl std::fmt::Display for BadAlgebraFileException {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "org.uacalc.io.BadAlgebraFileException: {}", self.message)
    }
}

impl std::error::Error for BadAlgebraFileException {
    fn description(&self) -> &str {
        &self.message
    }
}

use std::path::Path;
use once_cell::sync::Lazy;
use std::collections::HashSet;
use std::hash::{Hash, Hasher};

/// Filter files by extension.
/// 
/// This struct provides functionality to filter files based on their extensions,
/// similar to Java's FileFilter interface. It maintains a list of allowed extensions
/// and a description for display purposes.
/// 
/// # Examples
/// ```
/// use uacalc::io::ExtFileFilter;
/// use std::path::Path;
/// 
/// // Create filter for .ua files
/// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
/// 
/// // Check if a file should be accepted
/// let path = Path::new("example.ua");
/// assert!(filter.accept(path));
/// ```
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExtFileFilter {
    exts: HashSet<String>,
    description: String,
}

impl Hash for ExtFileFilter {
    fn hash<H: Hasher>(&self, state: &mut H) {
        // Convert HashSet to sorted Vec for consistent hashing
        let mut sorted_exts: Vec<&String> = self.exts.iter().collect();
        sorted_exts.sort();
        sorted_exts.hash(state);
        self.description.hash(state);
    }
}

/// Extension constants matching Java implementation
pub const ALG_EXT: &'static str = "alg";
pub const XML_EXT: &'static str = "xml";
pub const UAC_EXT: &'static str = "uac";
pub const UA_EXT: &'static str = "ua";
pub const CSV_EXT: &'static str = "csv";
pub const TXT_EXT: &'static str = "txt";

/// Static extension lists matching Java implementation
pub static UA_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec![UA_EXT.to_string(), XML_EXT.to_string()]
});

pub static ALL_ALG_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec![
        UA_EXT.to_string(),
        XML_EXT.to_string(),
        ALG_EXT.to_string(),
    ]
});

pub static MACE4_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec!["m4".to_string()]
});

impl ExtFileFilter {

    /// Creates a new `ExtFileFilter` with the given description and list of extensions.
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `exts` - Vector of allowed file extensions (without leading dots)
    /// 
    /// # Returns
    /// A new `ExtFileFilter` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    /// ```
    pub fn new(description: &str, exts: Vec<String>) -> Self {
        Self {
            exts: exts.into_iter().collect(),
            description: description.to_string(),
        }
    }

    /// Creates a new `ExtFileFilter` with the given description and single extension.
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `ext` - Single allowed file extension (without leading dot)
    /// 
    /// # Returns
    /// A new `ExtFileFilter` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_single("UA Files", "ua");
    /// ```
    pub fn new_single(description: &str, ext: &str) -> Self {
        Self {
            exts: vec![ext.to_string()].into_iter().collect(),
            description: description.to_string(),
        }
    }

    /// Creates a new `ExtFileFilter` with the given description and list of extensions (safe version).
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `exts` - Vector of allowed file extensions (without leading dots)
    /// 
    /// # Returns
    /// `Ok(ExtFileFilter)` - A new filter instance
    /// `Err(String)` - If validation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_safe("UA Files", vec!["ua".to_string()]).unwrap();
    /// ```
    pub fn new_safe(description: &str, exts: Vec<String>) -> Result<Self, String> {
        if description.is_empty() {
            return Err("Description cannot be empty".to_string());
        }
        if exts.is_empty() {
            return Err("Extensions list cannot be empty".to_string());
        }
        Ok(Self::new(description, exts))
    }

    /// Creates a new `ExtFileFilter` with the given description and single extension (safe version).
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `ext` - Single allowed file extension (without leading dot)
    /// 
    /// # Returns
    /// `Ok(ExtFileFilter)` - A new filter instance
    /// `Err(String)` - If validation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_single_safe("UA Files", "ua").unwrap();
    /// ```
    pub fn new_single_safe(description: &str, ext: &str) -> Result<Self, String> {
        if description.is_empty() {
            return Err("Description cannot be empty".to_string());
        }
        if ext.is_empty() {
            return Err("Extension cannot be empty".to_string());
        }
        Ok(Self::new_single(description, ext))
    }

    /// Determines whether the given file should be accepted by this filter.
    /// 
    /// # Arguments
    /// * `path` - The file path to check
    /// 
    /// # Returns
    /// `true` if the file should be accepted, `false` otherwise.
    /// Directories are always accepted.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// let path = Path::new("example.ua");
    /// assert!(filter.accept(path));
    /// 
    /// let path = Path::new("example.txt");
    /// assert!(!filter.accept(path));
    /// ```
    pub fn accept(&self, path: &Path) -> bool {
        // Always accept directories
        if path.is_dir() {
            return true;
        }
        
        // Check if file extension is in our allowed list
        if let Some(ext) = Self::get_extension(path) {
            self.exts.contains(&ext)
        } else {
            false
        }
    }

    /// Returns the description of this filter.
    /// 
    /// # Returns
    /// A reference to the description string
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// assert_eq!(filter.get_description(), "UA Files");
    /// ```
    pub fn get_description(&self) -> &str {
        &self.description
    }

    /// Returns the set of allowed extensions.
    /// 
    /// # Returns
    /// A reference to the set of allowed extensions
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// let exts = filter.get_extensions();
    /// assert!(exts.contains("ua"));
    /// ```
    pub fn get_extensions(&self) -> &HashSet<String> {
        &self.exts
    }

    /// Split the file name into 2 parts: the first everything up to the
    /// last "."; the rest the extension.
    ///
    /// # Arguments
    /// * `path` - The file path to split
    ///
    /// # Returns
    /// A tuple containing (filename_without_extension, extension) or (None, None) if no extension
    ///
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    ///
    /// let path = Path::new("example.ua");
    /// let (name, ext) = ExtFileFilter::split_off_extension(path);
    /// assert_eq!(name, Some("example".to_string()));
    /// assert_eq!(ext, Some("ua".to_string()));
    ///
    /// let path = Path::new("noextension");
    /// let (name, ext) = ExtFileFilter::split_off_extension(path);
    /// assert_eq!(name, None);
    /// assert_eq!(ext, None);
    /// ```
    pub fn split_off_extension(path: &Path) -> (Option<String>, Option<String>) {
        let filename = path.file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("");
        
        if let Some(last_dot) = filename.rfind('.') {
            if last_dot > 0 && last_dot < filename.len() - 1 {
                let name = filename[..last_dot].to_string();
                let ext = filename[last_dot + 1..].to_string();
                (Some(name), Some(ext))
            } else {
                (None, None)
            }
        } else {
            (None, None)
        }
    }

    /// Get the file extension from a file path.
    /// 
    /// # Arguments
    /// * `path` - The file path to get the extension from
    /// 
    /// # Returns
    /// `Some(extension)` if the file has an extension, `None` otherwise.
    /// The extension is returned without the leading dot.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    /// 
    /// let path = Path::new("example.ua");
    /// assert_eq!(ExtFileFilter::get_extension(path), Some("ua".to_string()));
    /// 
    /// let path = Path::new("noextension");
    /// assert_eq!(ExtFileFilter::get_extension(path), None);
    /// ```
    pub fn get_extension(path: &Path) -> Option<String> {
        let filename = path.file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("");
        
        if let Some(last_dot) = filename.rfind('.') {
            if last_dot > 0 && last_dot < filename.len() - 1 {
                Some(filename[last_dot + 1..].to_string())
            } else {
                None
            }
        } else {
            None
        }
    }
}

impl std::fmt::Display for ExtFileFilter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ExtFileFilter({})", self.description)
    }
}

pub struct JSONChannel {
    // TODO: Implement JSON channel
}

pub struct Mace4Reader {
    // TODO: Implement Mace4 reader
}
