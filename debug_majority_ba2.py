import sys
sys.path.insert(0, 'python')
import uacalc_lib

print("=" * 60)
print("Debugging majority_term for ba2.ua")
print("=" * 60)

# Load algebra
AlgebraReader = uacalc_lib.io.AlgebraReader
reader = AlgebraReader.new_from_file('resources/algebras/ba2.ua')
alg = reader.read_algebra_file()

print(f"\nAlgebra: {alg.name()}")
print(f"Cardinality: {alg.cardinality()}")
ops = alg.operations()
print(f"Number of operations: {len(ops)}")
for i, op in enumerate(ops):
    try:
        print(f"  Op {i}: {op.symbol()}, arity={op.arity()}")
    except:
        print(f"  Op {i}: (unable to get symbol/arity)")

# Test majority_term
print("\n" + "=" * 60)
print("Calling majority_term...")
print("=" * 60)

try:
    result = uacalc_lib.alg.majority_term(alg)
    print(f"\nResult: {result}")
    if result is None:
        print("❌ No majority term found (Java finds one!)")
    else:
        print(f"✓ Found term: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

