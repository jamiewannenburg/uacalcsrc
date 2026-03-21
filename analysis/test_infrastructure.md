# Analysis: Test Infrastructure Redundancy and Inefficiency

## 1. Redundant `run_java_wrapper` Definitions
The project currently defines `run_java_wrapper` (or similar variants) in **41 different Python files**. This leads to significant maintenance overhead and inconsistent error handling.

### Example of Redundancy:
Almost every file in `python/uacalc/tests/` contains a variation of this:
```python
def run_java_wrapper(wrapper_class: str, args):
    """Run Java wrapper and return JSON output."""
    cmd = build_java_command(wrapper_class, args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30.0)
        if result.returncode != 0:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
        return json.loads(result.stdout)
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
```

### Suggestion:
Centralize this in `python/uacalc/tests/test_utils.py` and import it. The current `test_utils.py` has a version that returns a `JavaCliOutput` object, while many tests expect a raw dictionary. These should be unified.

---

## 2. JVM Startup Overhead
The `compare_with_java!` macro in Rust and the `run_java_wrapper` function in Python both spawn a new JVM instance for every test. 

### Performance Impact:
- **Current:** ~200ms to 500ms per test just for JVM startup.
- **Scale:** 500 tests * 300ms = 150 seconds of pure overhead.

### Suggestion: persistent Java Bridge
Implement a simple "Test Server" in Java that stays alive during the test suite.
1. **Java side:** A simple socket server that listens for JSON requests, executes the requested class, and returns JSON.
2. **Rust/Python side:** A client that sends the arguments over the socket instead of calling `Command::new("java", ...)`.

**Example persistent bridge client (Conceptual):**
```rust
fn call_java_server(class: &str, args: Vec<String>) -> Value {
    let mut stream = TcpStream::connect("127.0.0.1:8080").unwrap();
    let request = json!({ "class": class, "args": args });
    serde_json::to_writer(&stream, &request).unwrap();
    serde_json::from_reader(&stream).unwrap()
}
```
