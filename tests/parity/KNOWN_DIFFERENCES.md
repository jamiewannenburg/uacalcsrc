# Known Differences Between Java and Python Implementations

This document records intentional differences between the Java UACalc implementation and the Rust/Python implementation.

**Important**: Only document differences here that are:
1. Intentional design decisions
2. Acceptable trade-offs
3. Python/Rust idiomatic improvements over Java

**Do NOT** document bugs here. Real mismatches should be fixed in the implementation.

---

## Format

For each difference:

```markdown
### package.ClassName.methodName

- **Java behavior**: Description
- **Python behavior**: Description
- **Reason**: Why this difference exists
- **Status**: Accepted / Under Review / To Be Fixed
- **Tracking**: Issue #123 (if applicable)
```

---

## Current Known Differences

### General Differences

#### Python `__repr__` vs Java default `toString()`

- **Java**: Default `toString()` often returns `ClassName@hexid` (memory address)
- **Python**: `__repr__()` returns useful debug info like `ClassName(field=value)`
- **Reason**: Python convention is to provide useful debug output
- **Status**: Accepted
- **Note**: Parity tests can skip string checks with `skip_string_check=True`

---

## org.uacalc.alg.Malcev

### minority_term / weak_nu_term

- **Java**: [Known behavior from Java UACalc]
- **Python**: [Current Rust implementation behavior]
- **Status**: Under Investigation
- **Note**: This is mentioned in the user requirements as a known mismatch that should fail visibly

---

## org.uacalc.io

### Exception messages for file operations

- **Java**: May include Java-specific stack traces or class names
- **Python**: Simplified error messages from Rust/PyO3
- **Reason**: Different error handling between Java and Rust
- **Status**: Accepted (as long as exception type matches)
- **Note**: Tests compare exception type primarily, messages secondarily

---

## org.uacalc.lat

### Lattice string representations

- **Java**: Often includes memory address
- **Python**: Includes cardinality and structural info
- **Reason**: More useful debug output
- **Status**: Accepted
- **Note**: Many lattice tests use `skip_string_check=True`

---

## Adding New Differences

When you discover an intentional difference:

1. **Verify** it's truly intentional, not a bug
2. **Document** it here with all required fields
3. **Update** test cases to handle it:
   - Set `skip_string_check=True` if string repr differs
   - Document expected vs actual behavior in test
4. **Link** to any relevant issues or discussions

Remember: The goal is 100% behavioral parity. Every difference here represents a deviation from that goal and should be justified.
