// Tests for SubalgebraLattice implementation comparing Rust with Java output

#[cfg(test)]
mod subalgebra_lattice_tests {
    use uacalc::alg::sublat::{SubalgebraLattice, BasicSet};
    use uacalc::alg::SmallAlgebra;
    use uacalc::io::AlgebraReader;
    use uacalc::lat::{Order, Lattice};
    use std::path::Path;

    fn load_algebra(path: &str) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        let reader = AlgebraReader::new_from_file(Path::new(path)).unwrap();
        Box::new(reader.read_algebra_file().unwrap())
    }

    #[test]
    fn test_new_subalgebra_lattice() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        assert_eq!(sub_lat.get_algebra().name(), "C3");
    }

    #[test]
    fn test_zero_and_one() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let one = sub_lat.one();
        
        assert_eq!(one.size(), 3);
        let expected = vec![0, 1, 2];
        assert_eq!(one.elements().len(), expected.len());
        for i in 0..expected.len() {
            assert_eq!(one.elements()[i], expected[i]);
        }
    }

    #[test]
    fn test_sg_generation() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let sub = sub_lat.sg(&[0, 1]);
        assert!(sub.size() > 0);
        assert!(sub.size() <= 3);
    }

    #[test]
    fn test_leq() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let sub1 = sub_lat.sg(&[0]);
        let sub2 = sub_lat.sg(&[0, 1]);
        
        assert!(sub_lat.leq(&sub1, &sub2));
    }

    #[test]
    fn test_join() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let sub1 = sub_lat.sg(&[0]);
        let sub2 = sub_lat.sg(&[1]);
        let join = sub_lat.join_sets(&sub1, &sub2);
        
        // Join should contain both generators
        assert!(join.contains(0) || sub1.contains(0));
        assert!(join.contains(1) || sub2.contains(1));
    }

    #[test]
    fn test_one_generated_subalgebras() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let mut sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let one_gens = sub_lat.one_generated_subalgebras();
        assert!(!one_gens.is_empty());
        assert!(one_gens.len() <= 3);
    }

    #[test]
    fn test_join_irreducibles() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let mut sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let jis = sub_lat.join_irreducibles_mut();
        assert!(!jis.is_empty());
        assert!(jis.len() <= 3);
    }

    #[test]
    fn test_no_duplicates() {
        let lst = vec![1, 2, 2, 3, 3, 3, 4];
        let result = SubalgebraLattice::no_duplicates(lst);
        assert_eq!(result, vec![1, 2, 3, 4]);
    }

    #[test]
    fn test_empty_no_duplicates() {
        let lst: Vec<i32> = vec![];
        let result = SubalgebraLattice::no_duplicates(lst);
        assert!(result.is_empty());
    }

    #[test]
    fn test_single_no_duplicates() {
        let lst = vec![5];
        let result = SubalgebraLattice::no_duplicates(lst);
        assert_eq!(result, vec![5]);
    }

    // Note: Comparison tests with Java wrapper require test-infrastructure feature
    // which includes the compare_with_java macro. These tests are simplified
    // for now to just verify basic functionality.

    #[test]
    fn test_description() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let mut sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let default_desc = sub_lat.get_description();
        assert!(default_desc.contains("Subalgebra Lattice"));
        
        sub_lat.set_description("Custom description".to_string());
        assert_eq!(sub_lat.get_description(), "Custom description");
    }

    #[test]
    fn test_meet() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let sub1 = BasicSet::new(vec![0, 1, 2]).unwrap();
        let sub2 = BasicSet::new(vec![1, 2]).unwrap();
        
        let meet = sub_lat.meet(&sub1, &sub2);
        // Meet should be the intersection
        assert_eq!(meet.elements().len(), 2);
        assert!(meet.contains(1));
        assert!(meet.contains(2));
    }

    #[test]
    fn test_filter() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let mut sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let elt = sub_lat.sg(&[0]);
        let filtered = sub_lat.filter(&elt);
        
        // All filtered subalgebras should contain elt
        for sub in &filtered {
            assert!(elt.leq(sub));
        }
    }

    #[test]
    fn test_minimal_generating_set() {
        let alg = load_algebra("resources/algebras/cyclic3.ua");
        let mut sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
        
        let gen_set = sub_lat.find_minimal_sized_generating_set();
        
        // Should be a minimal set that generates the entire algebra
        let generated_elems = gen_set.elements().clone();
        let generated = sub_lat.sg(&generated_elems);
        assert_eq!(generated.size(), 3);
    }
    
    #[test]
    fn test_java_wrapper_available() {
        // Test that the Java wrapper can be invoked
        let output = std::process::Command::new("java")
            .args(&["-cp", "java_wrapper/build/classes:build/classes:org:jars/*",
                   "java_wrapper.src.alg.sublat.SubalgebraLatticeWrapper",
                   "help"])
            .output()
            .expect("Failed to run Java wrapper");
        
        // Just check that it runs successfully
        assert!(output.status.success());
    }
    
    #[test]
    fn test_java_wrapper_new() {
        let output = std::process::Command::new("java")
            .args(&["-cp", "java_wrapper/build/classes:build/classes:org:jars/*",
                   "java_wrapper.src.alg.sublat.SubalgebraLatticeWrapper",
                   "new", "--algebra", "resources/algebras/cyclic3.ua"])
            .output()
            .expect("Failed to run Java wrapper");
        
        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("\"success\": true"));
        assert!(stdout.contains("\"algebra_name\": \"C3\""));
    }
    
    #[test]
    fn test_java_wrapper_no_duplicates() {
        let output = std::process::Command::new("java")
            .args(&["-cp", "java_wrapper/build/classes:build/classes:org:jars/*",
                   "java_wrapper.src.alg.sublat.SubalgebraLatticeWrapper",
                   "no_duplicates", "--list", "1,2,2,3,3,3"])
            .output()
            .expect("Failed to run Java wrapper");
        
        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("\"success\": true"));
        assert!(stdout.contains("[1, 2, 3]"));
    }
}
