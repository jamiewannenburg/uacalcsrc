use uacalc::util::virtuallist::virtuallists::*;

fn main() {
    match int_tuples(3, 4) {
        Ok(tuples) => {
            println!("IntTuples(3, 4) size: {}", tuples.size());
            for i in 0..tuples.size().min(5) {
                println!("  [{}]: {:?}", i, tuples.get(i));
            }
        }
        Err(e) => println!("Error: {}", e),
    }
}
