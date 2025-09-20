//! Lattice construction algorithms for building congruence universes
//!
//! This module provides efficient algorithms for constructing the complete
//! congruence lattice from join-irreducible elements.

use crate::algebra::SmallAlgebra;
use crate::conlat::principal::PrincipalCongruenceCache;
use crate::partition::{BasicPartition, Partition};
use crate::{UACalcError, UACalcResult};
use ahash::AHashMap;
use std::collections::HashSet;

#[cfg(feature = "parallel")]
use rayon::prelude::*;

/// Iterator for generating combinations without materializing the entire list
struct CombinationIterator {
    n: usize,
    k: usize,
    current: Option<Vec<usize>>,
    done: bool,
}

impl CombinationIterator {
    fn new(n: usize, k: usize) -> Self {
        if k > n || k == 0 {
            Self {
                n,
                k,
                current: None,
                done: true,
            }
        } else {
            let current = Some((0..k).collect::<Vec<_>>());
            Self {
                n,
                k,
                current,
                done: false,
            }
        }
    }
}

impl Iterator for CombinationIterator {
    type Item = Vec<usize>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }

        let result = self.current.clone()?;

        // Standard combination generation algorithm
        let mut i = self.k;
        while i > 0 && result[i - 1] == self.n - self.k + i - 1 {
            i -= 1;
        }

        if i == 0 {
            self.done = true;
            return Some(result);
        }

        let mut next = result.clone();
        next[i - 1] += 1;
        for j in i..self.k {
            next[j] = next[j - 1] + 1;
        }

        self.current = Some(next);
        Some(result)
    }
}

/// Builder for constructing congruence lattices from join-irreducibles
pub struct LatticeBuilder<'a> {
    algebra: &'a dyn SmallAlgebra,
    join_irreducibles: Vec<BasicPartition>,
    universe: Vec<BasicPartition>,
    principal_cache: AHashMap<(usize, usize), usize>, // Use AHashMap for better performance
    /// Cache for principal congruences to avoid recomputation
    principal_congruence_cache: PrincipalCongruenceCache<'a>,
    current_level: usize,
    max_level: usize,
    progress_callback: Option<Box<dyn super::ProgressCallback>>,
    /// Whether to use parallel processing
    parallel: bool,
    /// Canonical form cache for deduplication
    canonical_cache: AHashMap<u64, BasicPartition>,
}

impl<'a> LatticeBuilder<'a> {
    /// Create a new lattice builder for the given algebra
    pub fn new(algebra: &'a dyn SmallAlgebra) -> Self {
        let size = algebra.cardinality();
        Self {
            algebra,
            join_irreducibles: Vec::new(),
            universe: Vec::new(),
            principal_cache: AHashMap::new(),
            principal_congruence_cache: PrincipalCongruenceCache::new(algebra),
            current_level: 0,
            max_level: size * (size - 1) / 2, // Maximum possible JI's
            progress_callback: None,
            parallel: false,
            canonical_cache: AHashMap::new(),
        }
    }

    /// Set a progress callback for long-running constructions
    pub fn with_progress_callback(mut self, callback: Box<dyn super::ProgressCallback>) -> Self {
        self.progress_callback = Some(callback);
        self
    }

    /// Enable parallel processing
    pub fn with_parallel(mut self, parallel: bool) -> Self {
        self.parallel = parallel;
        self
    }

    /// Get access to the principal congruence cache for reuse
    pub fn principal_congruence_cache(&mut self) -> &mut PrincipalCongruenceCache<'a> {
        &mut self.principal_congruence_cache
    }

    /// Precompute all principal congruences for efficient reuse
    pub fn precompute_principal_congruences(&mut self) -> UACalcResult<()> {
        self.principal_congruence_cache.precompute_all()
    }

    /// Build the complete congruence universe
    pub fn build_universe(&mut self) -> UACalcResult<Vec<BasicPartition>> {
        let size = self.algebra.cardinality();

        // Start with bottom and top
        let bottom = BasicPartition::new(size);
        let top = self.create_coarsest_partition(size)?;

        self.universe = vec![bottom.clone(), top.clone()];

        // Find all join-irreducible congruences
        self.find_join_irreducibles()?;

        // Level-by-level construction
        self.construct_levels()?;

        // Remove duplicates and sort
        self.deduplicate_universe()?;

        Ok(self.universe.clone())
    }

    /// Find all join-irreducible congruences
    fn find_join_irreducibles(&mut self) -> UACalcResult<()> {
        let size = self.algebra.cardinality();

        // Precompute all principal congruences for efficient reuse
        self.principal_congruence_cache.precompute_all()?;

        // Generate all principal congruences θ(a,b) for a < b
        let mut principal_pairs = Vec::new();
        for a in 0..size {
            for b in (a + 1)..size {
                let principal = self
                    .principal_congruence_cache
                    .get_principal_congruence(a, b)?
                    .clone();

                // Check if this principal congruence is join-irreducible
                if self.is_join_irreducible(&principal)? {
                    self.join_irreducibles.push(principal);
                    principal_pairs.push((a, b));
                }
            }
        }

        // Sort by rank (number of blocks) for efficient level-by-level construction
        self.join_irreducibles
            .sort_by(|a, b| a.num_blocks().cmp(&b.num_blocks()));

        // Now populate the cache with correct indices after sorting
        for (a, b) in principal_pairs {
            // Find the index of this principal congruence in the sorted list
            let principal = self
                .principal_congruence_cache
                .get_principal_congruence(a, b)?;
            if let Some(index) = self.join_irreducibles.iter().position(|ji| ji == principal) {
                self.principal_cache.insert((a, b), index);
            }
        }

        Ok(())
    }

    /// Check if a congruence is join-irreducible
    ///
    /// Note: This implementation relies primarily on principal congruences for efficiency.
    /// It may misclassify non-principal lower covers in some cases. For a complete
    /// verification, one would need to check all congruences in the lattice, not just
    /// principal ones. This approximation is sufficient for most practical purposes
    /// where principal congruences are the primary source of join-irreducibles.
    fn is_join_irreducible(&mut self, congruence: &BasicPartition) -> UACalcResult<bool> {
        // A congruence is join-irreducible if it cannot be expressed as
        // the join of strictly smaller congruences

        // Basic checks
        if congruence.num_blocks() <= 1 {
            return Ok(false);
        }

        // Special case: the bottom partition (identity partition) is never join-irreducible
        // because it has no blocks to join (it's the minimal element)
        if congruence.num_blocks() == congruence.size() {
            return Ok(false);
        }

        // Early filtering: check if this is a principal congruence
        // Principal congruences are more likely to be join-irreducible
        let size = self.algebra.cardinality();
        let mut is_principal = false;
        let mut principal_pair = None;

        // Check if this congruence is a principal congruence
        for a in 0..size {
            for b in (a + 1)..size {
                let principal = self
                    .principal_congruence_cache
                    .get_principal_congruence(a, b)?;
                if principal == congruence {
                    is_principal = true;
                    principal_pair = Some((a, b));
                    break;
                }
            }
            if is_principal {
                break;
            }
        }

        // For principal congruences, use necessary conditions for early filtering
        if is_principal {
            // Check rank difference condition: if rank difference is 1, it's likely join-irreducible
            let rank_diff = size - congruence.num_blocks();
            if rank_diff == 1 {
                // This is a minimal pair - very likely join-irreducible
                // But we still need to verify it has at most one lower cover
                // Don't return early, continue with the full check
            }

            // Check if this principal congruence has a unique minimal pair
            if let Some((a, b)) = principal_pair {
                // Count how many other pairs generate the same congruence
                let mut same_congruence_count = 0;
                for c in 0..size {
                    for d in (c + 1)..size {
                        if (c, d) != (a, b) {
                            let other_principal = self
                                .principal_congruence_cache
                                .get_principal_congruence(c, d)?;
                            if other_principal == congruence {
                                same_congruence_count += 1;
                            }
                        }
                    }
                }

                // If this is the only pair generating this congruence, it's more likely join-irreducible
                if same_congruence_count == 0 {
                    // Still need to check for lower covers, but this is a good sign
                }
            }
        }

        // Find all congruences that are strictly finer than this one
        let mut lower_covers = Vec::new();
        let mut candidate_principals = Vec::new();

        // First pass: collect all principal congruences that are strictly finer
        for a in 0..size {
            for b in (a + 1)..size {
                let principal = self
                    .principal_congruence_cache
                    .get_principal_congruence(a, b)?;

                // Check if principal is strictly finer than congruence
                // Skip if they are identical (same congruence generated by different pairs)
                if *principal == *congruence {
                    continue;
                }
                
                if principal.is_finer_than(congruence)? && !congruence.is_finer_than(&*principal)? {
                    candidate_principals.push((a, b));
                }
            }
        }

        // Early exit: if no principal congruences are finer, this is join-irreducible
        if candidate_principals.is_empty() {
            return Ok(true);
        }

        // Second pass: check which candidates are actually lower covers
        for (a, b) in &candidate_principals {
            let principal = self
                .principal_congruence_cache
                .get_principal_congruence(*a, *b)?
                .clone();

            // Check if it's a lower cover (no congruence between them)
            let mut is_cover = true;

            // Only check against other candidate principals for efficiency
            for (c, d) in &candidate_principals {
                if (*c, *d) != (*a, *b) {
                    let other = self
                        .principal_congruence_cache
                        .get_principal_congruence(*c, *d)?
                        .clone();
                    if principal.is_finer_than(&other)?
                        && other.is_finer_than(congruence)?
                        && other != principal
                        && other != *congruence
                    {
                        is_cover = false;
                        break;
                    }
                }
            }

            if is_cover {
                lower_covers.push(principal);

                // Early exit: if we find more than one lower cover, it's not join-irreducible
                if lower_covers.len() > 1 {
                    return Ok(false);
                }
            }
        }

        // A congruence is join-irreducible if it has at most one lower cover
        Ok(lower_covers.len() <= 1)
    }

    /// Construct the lattice level by level
    fn construct_levels(&mut self) -> UACalcResult<()> {
        let mut level = 0;
        let mut new_congruences_found = true;

        while new_congruences_found && level < self.max_level {
            level += 1;
            new_congruences_found = false;

            // Report progress
            if let Some(ref callback) = self.progress_callback {
                let progress = level as f64 / self.max_level as f64;
                callback.report_progress(progress);

                if callback.should_cancel() {
                    return Err(UACalcError::Cancelled {
                        message: "Lattice construction was cancelled".to_string(),
                    });
                }
            }

            // Generate all joins of level congruences with join-irreducibles
            let level_congruences = self.generate_level_joins(level)?;

            // Add new congruences to universe
            for congruence in level_congruences {
                if !self.universe.contains(&congruence) {
                    self.universe.push(congruence);
                    new_congruences_found = true;
                }
            }
        }

        Ok(())
    }

    /// Generate all joins of k join-irreducibles
    fn generate_level_joins(&self, k: usize) -> UACalcResult<Vec<BasicPartition>> {
        let ji_count = self.join_irreducibles.len();

        if self.parallel {
            self.generate_level_joins_parallel(k, ji_count)
        } else {
            self.generate_level_joins_sequential(k, ji_count)
        }
    }

    /// Sequential version of generate_level_joins
    fn generate_level_joins_sequential(
        &self,
        k: usize,
        ji_count: usize,
    ) -> UACalcResult<Vec<BasicPartition>> {
        let mut joins = Vec::new();
        let mut seen_joins = HashSet::new();

        // Use iterator to generate combinations without materializing the entire list
        let mut combination_iter = CombinationIterator::new(ji_count, k);

        while let Some(combination) = combination_iter.next() {
            if combination.is_empty() {
                continue;
            }

            // Compute join of this combination
            let mut join = self.join_irreducibles[combination[0]].clone();
            for &ji_idx in &combination[1..] {
                // Use join operation to combine partitions
                join = join.join(&self.join_irreducibles[ji_idx])?;
            }

            // Deduplicate per level using canonical form
            let canonical = self.canonical_form(&join)?;
            if !seen_joins.contains(&canonical) {
                seen_joins.insert(canonical);
                joins.push(join);
            }
        }

        Ok(joins)
    }

    /// Parallel version of generate_level_joins
    #[cfg(feature = "parallel")]
    fn generate_level_joins_parallel(
        &self,
        k: usize,
        ji_count: usize,
    ) -> UACalcResult<Vec<BasicPartition>> {
        // Generate all combinations first (this is still sequential but necessary for parallel processing)
        let combinations: Vec<_> = CombinationIterator::new(ji_count, k).collect();

        // Process combinations in parallel
        let joins: UACalcResult<Vec<_>> = combinations
            .into_par_iter()
            .filter(|combination| !combination.is_empty())
            .map(|combination| {
                // Compute join of this combination
                let mut join = self.join_irreducibles[combination[0]].clone();
                for &ji_idx in &combination[1..] {
                    join = join.join(&self.join_irreducibles[ji_idx])?;
                }
                Ok(join)
            })
            .collect();

        joins
    }

    #[cfg(not(feature = "parallel"))]
    fn generate_level_joins_parallel(
        &self,
        k: usize,
        ji_count: usize,
    ) -> UACalcResult<Vec<BasicPartition>> {
        // Fallback to sequential if parallel feature is not enabled
        self.generate_level_joins_sequential(k, ji_count)
    }

    /// Generate all combinations of k elements from n elements
    fn generate_combinations(&self, n: usize, k: usize) -> Vec<Vec<usize>> {
        if k > n {
            return vec![];
        }

        if k == 0 {
            return vec![vec![]];
        }

        if k == 1 {
            return (0..n).map(|i| vec![i]).collect();
        }

        let mut combinations = Vec::new();
        let mut current = (0..k).collect::<Vec<_>>();

        loop {
            combinations.push(current.clone());

            // Generate next combination
            let mut i = k - 1;
            while i < k && current[i] == n - k + i {
                i = i.wrapping_sub(1);
            }

            if i >= k {
                break;
            }

            current[i] += 1;
            for j in (i + 1)..k {
                current[j] = current[j - 1] + 1;
            }
        }

        combinations
    }

    /// Remove duplicate congruences from universe
    fn deduplicate_universe(&mut self) -> UACalcResult<()> {
        let mut seen = HashSet::new();
        let mut unique = Vec::new();

        for congruence in &self.universe {
            let canonical = self.canonical_form(congruence)?;
            if seen.insert(canonical) {
                unique.push(congruence.clone());
            }
        }

        self.universe = unique;
        Ok(())
    }

    /// Create canonical form for partition comparison
    fn canonical_form(&self, partition: &BasicPartition) -> UACalcResult<Vec<Vec<usize>>> {
        let mut blocks = partition.blocks()?.to_vec();

        // Sort blocks by their smallest element
        blocks.sort_by(|a, b| {
            let min_a = a.iter().min().unwrap_or(&usize::MAX);
            let min_b = b.iter().min().unwrap_or(&usize::MAX);
            min_a.cmp(min_b)
        });

        // Sort elements within each block
        for block in &mut blocks {
            block.sort();
        }

        Ok(blocks)
    }

    /// Create the coarsest partition
    fn create_coarsest_partition(&self, size: usize) -> UACalcResult<BasicPartition> {
        let mut partition = BasicPartition::new(size);
        if size > 1 {
            for i in 1..size {
                partition.union(0, i)?;
            }
        }
        Ok(partition)
    }
}

/// Build the complete congruence universe for an algebra
pub fn build_universe(algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<BasicPartition>> {
    let mut builder = LatticeBuilder::new(algebra);
    builder.build_universe()
}

/// Find all join-irreducible congruences for an algebra
pub fn find_join_irreducibles(algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<BasicPartition>> {
    let mut builder = LatticeBuilder::new(algebra);
    builder.find_join_irreducibles()?;
    Ok(builder.join_irreducibles)
}

/// Check if a congruence is join-irreducible
pub fn is_join_irreducible(
    algebra: &dyn SmallAlgebra,
    congruence: &BasicPartition,
) -> UACalcResult<bool> {
    let mut builder = LatticeBuilder::new(algebra);
    builder.is_join_irreducible(congruence)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::algebra::BasicAlgebra;
    use crate::operation::{OperationSymbol, TableOperation};

    #[test]
    fn test_combination_iterator() {
        // Test (3,2) combinations
        let iter = CombinationIterator::new(3, 2);
        let combinations: Vec<Vec<usize>> = iter.collect();
        assert_eq!(combinations, vec![vec![0, 1], vec![0, 2], vec![1, 2],]);

        // Test (4,2) combinations
        let iter = CombinationIterator::new(4, 2);
        let combinations: Vec<Vec<usize>> = iter.collect();
        assert_eq!(
            combinations,
            vec![
                vec![0, 1],
                vec![0, 2],
                vec![0, 3],
                vec![1, 2],
                vec![1, 3],
                vec![2, 3],
            ]
        );

        // Test (3,3) combinations
        let iter = CombinationIterator::new(3, 3);
        let combinations: Vec<Vec<usize>> = iter.collect();
        assert_eq!(combinations, vec![vec![0, 1, 2]]);

        // Test invalid combinations
        let iter = CombinationIterator::new(2, 3); // k > n
        let combinations: Vec<Vec<usize>> = iter.collect();
        assert_eq!(combinations, Vec::<Vec<usize>>::new());

        let iter = CombinationIterator::new(3, 0); // k = 0
        let combinations: Vec<Vec<usize>> = iter.collect();
        assert_eq!(combinations, Vec::<Vec<usize>>::new());
    }

    #[test]
    fn test_build_universe_trivial() {
        let algebra = BasicAlgebra::new("test".to_string(), vec![0, 1, 2]).unwrap();
        let universe = build_universe(&algebra);
        assert!(universe.is_ok());
        let universe = universe.unwrap();
        // For a trivial algebra with no operations, we expect:
        // 1. Bottom partition (identity): [[0], [1], [2]]
        // 2. Top partition (universal): [[0, 1, 2]]
        // 3. Three principal congruences: [[0,1], [2]], [[0,2], [1]], [[0], [1,2]]
        // So total should be 5, not 2
        assert_eq!(universe.len(), 5); // Bottom, top, and 3 principal congruences
    }

    #[test]
    fn test_find_join_irreducibles() {
        let algebra = BasicAlgebra::new("test".to_string(), vec![0, 1, 2]).unwrap();
        let jis = find_join_irreducibles(&algebra);
        assert!(jis.is_ok());
        let jis = jis.unwrap();
        assert_eq!(jis.len(), 3); // θ(0,1), θ(0,2), θ(1,2)
    }

    #[test]
    fn test_is_join_irreducible() {
        let algebra = BasicAlgebra::new("test".to_string(), vec![0, 1, 2]).unwrap();
        let partition = BasicPartition::new(3);
        let result = is_join_irreducible(&algebra, &partition);
        assert!(result.is_ok());
        assert!(!result.unwrap()); // Bottom is not join-irreducible
    }
}
