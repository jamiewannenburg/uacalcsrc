pub mod virtuallist;
pub mod horner;
pub mod simple_list;
pub mod array_string;
pub mod permutation_generator;
pub mod array_incrementor;
pub mod int_array;

pub use permutation_generator::PermutationGenerator;
pub use array_incrementor::{ArrayIncrementor, ArrayIncrementorImpl, SimpleArrayIncrementor};
pub use int_array::{IntArrayTrait, IntArray};
pub use virtuallist::{
    LongList, IntTuples, IntTuplesWithMin, FixedSizedSubsets, Subsets, Permutations, LongListUtils
};
