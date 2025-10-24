use uacalc::util::virtuallist::virtuallists::*;

fn main() {
    // Test what IntTuplesWithMin produces
    match int_tuples_with_min(3, 4, 2) {
        Ok(tuples) => {
            println!("IntTuplesWithMin(3, 4, 2) size: {}", tuples.size());
            for i in 0..tuples.size().min(5) {
                println!("  [{}]: {:?}", i, tuples.get(i));
            }
        }
        Err(e) => println!("Error: {}", e),
    }
    
    // Test what array_indexer_with_min produces
    match array_indexer_with_min(0, 3, 4, 2) {
        Ok(arr) => println!("array_indexer_with_min(0, 3, 4, 2): {:?}", arr),
        Err(e) => println!("Error: {}", e),
    }
}
