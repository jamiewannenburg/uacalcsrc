/*!
 * Test for ConLyndonF3 example.
 * 
 * This test replicates the functionality of ConLyndonF3.java:
 * - Loads lyndon.ua algebra
 * - Creates a FreeAlgebra with 4 generators
 * - Gets the congruence lattice
 * - Prints cardinalities and meet irreducibles
 */

#[cfg(test)]
mod tests {
    use std::path::Path;
    use uacalc::io::algebra_io::read_algebra_file;
    use uacalc::alg::free_algebra::FreeAlgebra;
    use uacalc::alg::SmallAlgebra;
    use uacalc::alg::Algebra;
    
    /// Test ConLyndonF3 similar to ConLyndonF3.java
    /// 
    /// This test loads lyndon.ua, creates a FreeAlgebra with 4 generators,
    /// gets the congruence lattice, and prints meet irreducibles.
    #[test]
    fn test_con_lyndon_f3() {
        // Path to algebra file
        let alg0_file = Path::new("resources/algebras/lyndon.ua");
        
        // Check if file exists
        if !alg0_file.exists() {
            eprintln!("Skipping test: {} not found", alg0_file.display());
            return;
        }
        
        // Load algebra
        let alg0 = read_algebra_file(alg0_file)
            .expect("Failed to read alg0 file");
        
        println!("Loaded algebra: {} (size: {})", alg0.name(), alg0.cardinality());
        
        let number_of_gens = 4;
        
        // Create FreeAlgebra with decompose=true, idempotent=true, total=true
        // Note: Rust API might differ - checking available constructors
        let fr = FreeAlgebra::new_with_decompose_safe(
            format!("F({})", number_of_gens),
            alg0,
            number_of_gens,
            true,  // idempotent
            true,  // total
            true,  // decompose
            None,  // term_map
            None,  // report
        ).expect("Failed to create FreeAlgebra");
        
        println!("|F({})| = {}", number_of_gens, fr.cardinality());
        
        // Get congruence lattice
        // Note: FreeAlgebra uses IntArray as UniverseItem, not i32
        // We need to create congruence lattice for IntArray type
        use uacalc::alg::conlat::CongruenceLattice;
        use uacalc::util::int_array::IntArray;
        
        // Get the free algebra as a SmallAlgebra to create congruence lattice
        // FreeAlgebra's UniverseItem is IntArray, not i32
        let fr_box: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = fr.clone_box();
        let mut con = CongruenceLattice::new(fr_box);
        
        let con_card = con.con_cardinality();
        println!("|Con(F({}))| = {}", number_of_gens, con_card);
        
        // Get meet irreducibles
        let mis = con.meet_irreducibles();
        
        let mut k = 0;
        for part in mis {
            print!("{}: {}", k, part);
            println!("  {} blocks", part.number_of_blocks());
            k += 1;
        }
    }
    
    /// Test with a simpler algebra to verify basic functionality
    #[test]
    fn test_con_lyndon_f3_simple() {
        let alg_file = Path::new("resources/algebras/cyclic3.ua");
        
        if !alg_file.exists() {
            eprintln!("Skipping test: algebra file not found");
            return;
        }
        
        let alg = read_algebra_file(alg_file)
            .expect("Failed to read algebra file");
        
        let number_of_gens = 2;
        
        let fr = FreeAlgebra::new_with_decompose_safe(
            format!("F({})", number_of_gens),
            alg,
            number_of_gens,
            true,
            true,
            true,
            None,
            None,
        ).expect("Failed to create FreeAlgebra");
        
        println!("FreeAlgebra cardinality: {}", fr.cardinality());
        
        use uacalc::alg::conlat::CongruenceLattice;
        use uacalc::util::int_array::IntArray;
        let fr_box: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = fr.clone_box();
        let mut con = CongruenceLattice::new(fr_box);
        
        let con_card = con.con_cardinality();
        println!("Congruence lattice cardinality: {}", con_card);
        
        let mis = con.meet_irreducibles();
        println!("Number of meet irreducibles: {}", mis.len());
    }
}

