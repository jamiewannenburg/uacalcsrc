//! Free and finitely presented lattices module.
//!
//! This module provides functionality for working with free and finitely presented lattices
//! as defined in Grätzer's "Structure and Topology in Algebra" book.

pub mod partially_defined_lattice;

pub use partially_defined_lattice::{PartiallyDefinedLattice, main as partially_defined_lattice_main};