use pyo3::prelude::*;

pub mod alg;
pub mod element;
pub mod eq;
pub mod example;
pub mod fplat;
pub mod group;
pub mod io;
pub mod lat;
pub mod terms;
pub mod types;
pub mod util;

/// A Python module implemented in Rust.
#[pymodule]
fn uacalc_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    // Algebra module
    let alg_module = PyModule::new(_py, "alg")?;
    alg::register_alg_module(_py, alg_module)?;
    m.add_submodule(alg_module)?;

    // Element module
    let element_module = PyModule::new(_py, "element")?;
    element::register_element_module(_py, element_module)?;
    m.add_submodule(element_module)?;

    // Equation module
    let eq_module = PyModule::new(_py, "eq")?;
    eq::register_eq_module(_py, eq_module)?;
    m.add_submodule(eq_module)?;

    // Example module
    let example_module = PyModule::new(_py, "example")?;
    example::register_example_module(_py, example_module)?;
    m.add_submodule(example_module)?;

    // Fplat module
    let fplat_module = PyModule::new(_py, "fplat")?;
    fplat::register_fplat_module(_py, fplat_module)?;
    m.add_submodule(fplat_module)?;

    // Group module
    let group_module = PyModule::new(_py, "group")?;
    group::register_group_module(_py, group_module)?;
    m.add_submodule(group_module)?;

    // IO module
    let io_module = PyModule::new(_py, "io")?;
    io::register_io_module(_py, io_module)?;
    m.add_submodule(io_module)?;

    // Lattice module
    let lat_module = PyModule::new(_py, "lat")?;
    lat::register_lat_module(_py, lat_module)?;
    m.add_submodule(lat_module)?;

    // Terms module
    let terms_module = PyModule::new(_py, "terms")?;
    terms::register_terms_module(_py, terms_module)?;
    m.add_submodule(terms_module)?;

    // Util module
    let util_module = PyModule::new(_py, "util")?;
    util::register_util_module(_py, util_module)?;
    m.add_submodule(util_module)?;

    // Types module
    let types_module = PyModule::new(_py, "types")?;
    types::register_types_module(_py, types_module)?;
    m.add_submodule(types_module)?;

    Ok(())
}
