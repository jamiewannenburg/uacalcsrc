use std::fmt::{Display, Debug};
use crate::alg::Algebra;

/// Trait representing an element in an algebra.
/// 
/// This trait provides the interface for elements that belong to algebras in UACalc.
/// Elements have:
/// - An associated algebra they belong to
/// - An index within that algebra's universe
/// - Optional parent relationships for hierarchical structures
/// 
/// # Implementation Notes
/// 
/// Concrete implementations like `SubProductElement` should implement this trait.
/// The trait uses dynamic dispatch through `dyn Element` to allow polymorphic usage.
/// 
/// # Examples
/// 
/// ```ignore
/// // This example requires a concrete implementation like SubProductElement
/// use uacalc::element::Element;
/// 
/// fn print_element_info(elem: &dyn Element) {
///     println!("Element index: {}", elem.index());
///     println!("Algebra: {}", elem.get_algebra());
/// }
/// ```
pub trait Element: Display + Debug + Send + Sync {
    /// Returns the algebra this element belongs to.
    /// 
    /// # Returns
    /// A reference to the algebra containing this element
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let element = ...; // Create an element
    /// let algebra = element.get_algebra();
    /// println!("Element belongs to algebra: {}", algebra.name());
    /// ```
    fn get_algebra(&self) -> &dyn Algebra<UniverseItem = i32>;
    
    /// Returns the index of this element in the algebra's universe.
    /// 
    /// The index is a unique identifier for this element within its algebra.
    /// For finite algebras, this is typically a value from 0 to cardinality-1.
    /// 
    /// # Returns
    /// The index of this element as an integer
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let element = ...; // Create an element
    /// let idx = element.index();
    /// println!("Element index: {}", idx);
    /// ```
    fn index(&self) -> i32;
    
    /// Returns the parent element of this element, if any.
    /// 
    /// For elements in hierarchical structures (like subproducts), this returns
    /// the parent element from which this element was derived. Returns `None`
    /// if this element has no parent.
    /// 
    /// # Returns
    /// - `Some(parent)` if this element has a parent
    /// - `None` if this element has no parent
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let element = ...; // Create an element
    /// if let Some(parent) = element.get_parent() {
    ///     println!("Parent element index: {}", parent.index());
    /// } else {
    ///     println!("This element has no parent");
    /// }
    /// ```
    fn get_parent(&self) -> Option<&dyn Element>;
    
    /// Returns an array of parent elements, if any.
    /// 
    /// For elements that may have multiple parents in a hierarchical structure,
    /// this returns all parent elements. Returns `None` if there are no parents.
    /// 
    /// # Returns
    /// - `Some(parents)` if this element has parent elements
    /// - `None` if this element has no parents
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let element = ...; // Create an element
    /// if let Some(parents) = element.get_parent_array() {
    ///     for parent in parents {
    ///         println!("Parent index: {}", parent.index());
    ///     }
    /// }
    /// ```
    fn get_parent_array(&self) -> Option<&[Box<dyn Element>]>;
    
    /// Returns an array of parent element indices, if any.
    /// 
    /// This is a more efficient alternative to `get_parent_array()` when only
    /// the indices are needed, avoiding the need to return element references.
    /// 
    /// # Returns
    /// - `Some(indices)` if this element has parent elements
    /// - `None` if this element has no parents
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let element = ...; // Create an element
    /// if let Some(indices) = element.parent_index_array() {
    ///     println!("Parent indices: {:?}", indices);
    /// } else {
    ///     println!("No parent indices");
    /// }
    /// ```
    fn parent_index_array(&self) -> Option<&[i32]>;
}

/// Helper trait for cloning elements.
/// 
/// Since we can't have `Clone` in the main Element trait due to object safety,
/// we provide this separate trait for cloning elements when needed.
pub trait CloneableElement: Element {
    /// Clone this element into a boxed trait object.
    /// 
    /// # Returns
    /// A boxed clone of this element
    fn clone_box(&self) -> Box<dyn CloneableElement>;
}

impl<T> CloneableElement for T
where
    T: 'static + Element + Clone,
{
    fn clone_box(&self) -> Box<dyn CloneableElement> {
        Box::new(self.clone())
    }
}

/// Type alias for boxed elements for convenience.
pub type BoxedElement = Box<dyn Element>;

/// Create a boxed element from any type implementing Element.
/// 
/// # Arguments
/// * `elem` - The element to box
/// 
/// # Returns
/// A boxed element trait object
/// 
/// # Examples
/// 
/// ```ignore
/// let element = ...; // Create an element
/// let boxed = boxed_element(element);
/// ```
pub fn boxed_element<T: 'static + Element>(elem: T) -> BoxedElement {
    Box::new(elem)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // Mock element for testing
    #[derive(Clone, Debug)]
    struct MockElement {
        index_val: i32,
    }
    
    impl Display for MockElement {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "MockElement[{}]", self.index_val)
        }
    }
    
    // We can't fully implement Element without a mock Algebra,
    // but we can test the trait structure compiles
    
    #[test]
    fn test_trait_exists() {
        // This test just verifies the trait compiles
        assert!(true);
    }
}

pub struct SubProductElement {
    // TODO: Implement subproduct element
}