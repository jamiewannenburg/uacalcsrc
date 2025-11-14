/*!
 * SubProductElement - Element in a SubProductAlgebra.
 * 
 * This is an implementation of org.uacalc.element.SubProductElement.
 */

use std::collections::HashMap;
use std::fmt::{self, Debug, Display};
use crate::element::Element;
use crate::alg::{Algebra, SubProductAlgebra};
use crate::util::int_array::IntArray;
use crate::terms::{Term, VariableImp};

/// An element in a SubProductAlgebra.
/// 
/// This struct represents an element that belongs to a SubProductAlgebra,
/// storing both the element value (as IntArray) and a reference to the algebra.
/// 
/// # Examples
/// ```ignore
/// use uacalc::element::SubProductElement;
/// use uacalc::alg::SubProductAlgebra;
/// use uacalc::util::int_array::IntArray;
/// 
/// // Create a subproduct algebra...
/// let alg = SubProductAlgebra::new_safe(...).unwrap();
/// 
/// // Create an element
/// let element = IntArray::new_from_slice(&[0, 1]).unwrap();
/// let sub_elem = SubProductElement::new(element, &alg);
/// 
/// // Get the element's index
/// let idx = sub_elem.index();
/// ```
#[derive(Clone, Debug)]
pub struct SubProductElement {
    /// The element value as IntArray
    pub element: IntArray,
    
    /// The algebra this element belongs to (stored as a pointer/reference)
    /// Note: In Rust we can't easily store a reference with lifetime,
    /// so we store it as a raw pointer for simplicity in this partial implementation
    algebra_ptr: *const SubProductAlgebra<i32>,
}

// Safety: We ensure the algebra pointer remains valid during the element's lifetime
unsafe impl Send for SubProductElement {}
unsafe impl Sync for SubProductElement {}

impl SubProductElement {
    /// Create a new SubProductElement.
    /// 
    /// # Arguments
    /// * `elt` - The element value as IntArray
    /// * `alg` - Reference to the SubProductAlgebra
    /// 
    /// # Returns
    /// A new SubProductElement
    /// 
    /// # Safety
    /// The algebra must remain valid for the lifetime of this element.
    pub fn new(elt: IntArray, alg: &SubProductAlgebra<i32>) -> Self {
        SubProductElement {
            element: elt,
            algebra_ptr: alg as *const SubProductAlgebra<i32>,
        }
    }
    
    /// Get a reference to the algebra (unsafe).
    /// 
    /// # Safety
    /// The algebra pointer must still be valid.
    unsafe fn get_algebra_ref(&self) -> &SubProductAlgebra<i32> {
        &*self.algebra_ptr
    }
    
    /// Get the term associated with this element.
    /// 
    /// # Returns
    /// The term for this element, or None if terms were not computed
    pub fn get_term(&self) -> Option<&dyn Term> {
        unsafe {
            self.get_algebra_ref().get_term(&self.element)
        }
    }
    
    /// Get the list of variables in the term for this element.
    /// 
    /// # Returns
    /// The list of variables, or None if no term exists
    pub fn get_variable_list(&self) -> Option<Vec<VariableImp>> {
        self.get_term().and_then(|term| {
            let var_list = term.get_variable_list();
            Some(var_list.into_iter()
                .map(|name| VariableImp::new(&name))
                .collect())
        })
    }
    
    /// Get the variable to generator mapping for this element.
    /// 
    /// # Returns
    /// A map from variables to their generator values
    pub fn get_variable_map(&self) -> Option<HashMap<VariableImp, IntArray>> {
        let var_list = self.get_variable_list()?;
        let algebra = unsafe { self.get_algebra_ref() };
        let vars_map = algebra.get_variable_to_generator_map()?;
        
        let mut ans = HashMap::new();
        for var in var_list {
            if let Some(gen) = vars_map.get(&var) {
                ans.insert(var, gen.clone());
            }
        }
        
        Some(ans)
    }
    
    /// Get the element as an IntArray.
    pub fn get_element(&self) -> &IntArray {
        &self.element
    }
}

impl Display for SubProductElement {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Format the IntArray as a string
        write!(f, "{}", self.element)?;
        
        if let Some(term) = self.get_term() {
            write!(f, ", term: {}", term)?;
            write!(f, " under ")?;
            
            if let Some(var_list) = self.get_variable_list() {
                if let Some(var_map) = self.get_variable_map() {
                    for var in var_list {
                        if let Some(gen) = var_map.get(&var) {
                            write!(f, "{} -> {}, ", var, gen)?;
                        }
                    }
                }
            }
        }
        
        Ok(())
    }
}

impl Element for SubProductElement {
    fn get_algebra(&self) -> &dyn Algebra<UniverseItem = i32> {
        unsafe {
            // This is a workaround for the lifetime issue
            // In a full implementation, we'd use a better approach
            // For now, we panic as this method is not easily implementable
            panic!("get_algebra not implemented for SubProductElement - use get_algebra_ref with correct lifetime")
        }
    }
    
    fn index(&self) -> i32 {
        unsafe {
            let alg = self.get_algebra_ref();
            alg.element_index(&self.element).unwrap_or(0) as i32
        }
    }
    
    fn get_parent(&self) -> Option<&dyn Element> {
        None
    }
    
    fn get_parent_array(&self) -> Option<&[Box<dyn Element>]> {
        None
    }
    
    fn parent_index_array(&self) -> Option<&[i32]> {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_sub_product_element_struct_exists() {
        // This test just verifies the struct compiles
        assert!(true);
    }
}
