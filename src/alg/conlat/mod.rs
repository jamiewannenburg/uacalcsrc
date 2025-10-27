/// Congruence lattice algorithms and data structures.
/// 
/// This module contains implementations for working with congruence lattices,
/// including partition representations and related algorithms.

pub mod binary_relation;
pub mod basic_binary_relation;
pub mod partition;
pub mod polymorphisms;
pub mod subtrace;
pub mod congruence_lattice;
pub mod type_finder;

pub use binary_relation::{
    BinaryRelation, MutableBinaryRelation, BinaryRelationCompare, 
    BinaryRelationIterator, BinaryRelationFactory
};
pub use basic_binary_relation::BasicBinaryRelation;
pub use partition::{Partition, PrintType};
pub use polymorphisms::Polymorphisms;
pub use subtrace::Subtrace;
pub use congruence_lattice::{CongruenceLattice, MAX_DRAWABLE_SIZE, MAX_DRAWABLE_INPUT_SIZE};
pub use type_finder::TypeFinder;