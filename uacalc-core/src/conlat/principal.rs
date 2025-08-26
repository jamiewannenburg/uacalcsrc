//! Principal congruence computation and caching
//!
//! This module provides efficient computation and caching of principal
//! congruences θ(a, b) for pairs of elements.

use crate::algebra::SmallAlgebra;
use crate::conlat::cg::principal_congruence;
use crate::partition::{BasicPartition, Partition};
use crate::{UACalcError, UACalcResult};
use std::collections::HashMap;

/// Cache for principal congruences to avoid recomputation
pub struct PrincipalCongruenceCache<'a> {
    algebra: &'a dyn SmallAlgebra,
    cache: HashMap<(usize, usize), BasicPartition>,
}

impl<'a> PrincipalCongruenceCache<'a> {
    /// Create a new principal congruence cache
    pub fn new(algebra: &'a dyn SmallAlgebra) -> Self {
        Self {
            algebra,
            cache: HashMap::new(),
        }
    }

    /// Get the principal congruence θ(a, b), computing it if not cached
    pub fn get_principal_congruence(
        &mut self,
        a: usize,
        b: usize,
    ) -> UACalcResult<&BasicPartition> {
        let key = if a < b { (a, b) } else { (b, a) };

        if !self.cache.contains_key(&key) {
            let congruence = principal_congruence(self.algebra, key.0, key.1)?;
            self.cache.insert(key, congruence);
        }

        Ok(&self.cache[&key])
    }

    /// Precompute all principal congruences for the algebra
    pub fn precompute_all(&mut self) -> UACalcResult<()> {
        let size = self.algebra.cardinality();

        for a in 0..size {
            for b in (a + 1)..size {
                self.get_principal_congruence(a, b)?;
            }
        }

        Ok(())
    }

    /// Get all cached principal congruences
    pub fn all_principal_congruences(&self) -> Vec<BasicPartition> {
        self.cache.values().cloned().collect()
    }

    /// Clear the cache
    pub fn clear(&mut self) {
        self.cache.clear();
    }

    /// Get cache statistics
    pub fn cache_stats(&self) -> (usize, usize) {
        let size = self.algebra.cardinality();
        let total_pairs = size * (size - 1) / 2;
        (self.cache.len(), total_pairs)
    }
}

/// Compute the principal congruence θ(a, b) with caching
pub fn principal_congruence_cached(
    algebra: &dyn SmallAlgebra,
    a: usize,
    b: usize,
) -> UACalcResult<BasicPartition> {
    let mut cache = PrincipalCongruenceCache::new(algebra);
    cache.get_principal_congruence(a, b).map(|p| p.clone())
}

/// Compute all principal congruences for an algebra
pub fn all_principal_congruences(algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<BasicPartition>> {
    let mut cache = PrincipalCongruenceCache::new(algebra);
    cache.precompute_all()?;
    Ok(cache.all_principal_congruences())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::algebra::BasicAlgebra;

    #[test]
    fn test_principal_congruence_cache() {
        let algebra = BasicAlgebra::new("test".to_string(), vec![0, 1, 2]).unwrap();
        let mut cache = PrincipalCongruenceCache::new(&algebra);

        let congruence = cache.get_principal_congruence(0, 1);
        assert!(congruence.is_ok());

        let stats = cache.cache_stats();
        assert_eq!(stats.0, 1); // One cached
        assert_eq!(stats.1, 3); // Total pairs for size 3
    }

    #[test]
    fn test_precompute_all() {
        let algebra = BasicAlgebra::new("test".to_string(), vec![0, 1, 2]).unwrap();
        let mut cache = PrincipalCongruenceCache::new(&algebra);

        let result = cache.precompute_all();
        assert!(result.is_ok());

        let stats = cache.cache_stats();
        assert_eq!(stats.0, 3); // All pairs cached
        assert_eq!(stats.1, 3); // Total pairs
    }
}
