use uacalc_core::prelude::*;
use uacalc_core::operation::TableOperation;
use uacalc_core::operation::OperationSymbol;

fn main() -> UACalcResult<()> {
    println!("UACalc Core Example");
    
    // Create a simple algebra
    let mut algebra = BasicAlgebra::new("ExampleAlgebra".to_string(), vec![0, 1, 2]);
    
    // Create a binary operation (addition modulo 3)
    let symbol = OperationSymbol::new("add".to_string(), 2);
    let table = vec![
        vec![0, 1, 2],  // 0 + x
        vec![1, 2, 0],  // 1 + x
        vec![2, 0, 1],  // 2 + x
    ];
    
    let operation = TableOperation::new(symbol, table)?;
    algebra.add_operation("add".to_string(), Arc::new(operation))?;
    
    println!("Created algebra: {}", algebra.name());
    println!("Universe: {:?}", algebra.universe());
    println!("Cardinality: {}", algebra.cardinality());
    println!("Number of operations: {}", algebra.operations().len());
    
    // Test the operation
    if let Some(op) = algebra.operations().first() {
        println!("Testing operation: {}", op.symbol().name);
        println!("0 + 1 = {}", op.value(&[0, 1])?);
        println!("1 + 2 = {}", op.value(&[1, 2])?);
        println!("2 + 2 = {}", op.value(&[2, 2])?);
    }
    
    Ok(())
}

