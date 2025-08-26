use uacalc_core::prelude::*;
use uacalc_core::operation::TableOperation;
use uacalc_core::operation::OperationSymbol;

fn main() -> UACalcResult<()> {
    println!("UACalc Core Example");
    
    // Create a simple algebra
    let mut algebra = BasicAlgebra::new("ExampleAlgebra".to_string(), vec![0, 1, 2])?;
    
    // Create a binary operation (addition modulo 3)
    let symbol = OperationSymbol::new("add".to_string(), 2);
    let table = vec![
        vec![0, 0, 0],  // 0 + 0 = 0
        vec![0, 1, 1],  // 0 + 1 = 1
        vec![0, 2, 2],  // 0 + 2 = 2
        vec![1, 0, 1],  // 1 + 0 = 1
        vec![1, 1, 2],  // 1 + 1 = 2
        vec![1, 2, 0],  // 1 + 2 = 0
        vec![2, 0, 2],  // 2 + 0 = 2
        vec![2, 1, 0],  // 2 + 1 = 0
        vec![2, 2, 1],  // 2 + 2 = 1
    ];
    
    let operation = TableOperation::new(symbol, table, 3)?;
    algebra.add_operation_simple(operation)?;
    
    println!("Created algebra: {}", algebra.name());
    println!("Universe: {:?}", algebra.universe());
    println!("Cardinality: {}", algebra.cardinality());
    println!("Number of operations: {}", algebra.operations().len());
    
    // Test the operation using the new with_operation method
    algebra.with_operation_by_symbol("add", |op| {
        println!("Testing operation: {}", op.symbol().name);
        println!("0 + 1 = {}", op.value(&[0, 1])?);
        println!("1 + 2 = {}", op.value(&[1, 2])?);
        println!("2 + 2 = {}", op.value(&[2, 2])?);
        Ok(())
    })?;
    
    Ok(())
}

