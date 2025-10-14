//! Lattice and ordered set algorithms.
//!
//! This module provides algorithms for working with ordered sets and lattices,
//! ported from the Java UACalc implementation.

pub mod order;
pub mod ordered_sets;

pub use order::Order;
pub use ordered_sets::{maximals, main as ordered_sets_main};