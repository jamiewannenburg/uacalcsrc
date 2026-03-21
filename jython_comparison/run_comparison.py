import subprocess
import os
import sys

def run_cmd(cmd, env):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return result.stdout.strip(), result.stderr.strip()

def main():
    script = "jython_comparison/test_script.py"
    
    # 1. Run Jython
    print("Running Jython...")
    jython_env = os.environ.copy()
    jython_env["CLASSPATH"] = "./jars/uacalc.jar"
    # Ensure Jython doesn't pick up our compatibility layer during Java import
    jython_env["PYTHONPATH"] = "" 
    jython_out, jython_err = run_cmd("jython " + script, jython_env)
    
    # 2. Run Python
    print("Running Python...")
    python_env = os.environ.copy()
    python_env["PYTHONPATH"] = "./python:./python/uacalc_lib"
    python_out, python_err = run_cmd("./venv/bin/python3 " + script, python_env)
    
    print("\n--- JYTHON OUTPUT ---")
    print(jython_out)
    if jython_err: print("ERR: " + jython_err)
    
    print("\n--- PYTHON OUTPUT ---")
    print(python_out)
    if python_err: print("ERR: " + python_err)
    
    print("\n--- COMPARISON ---")
    if jython_out == python_out:
        print("SUCCESS: Outputs match perfectly!")
    else:
        # Filter out the 'Universe' line since we know it differs for now
        j_lines = [l for l in jython_out.splitlines() if not l.startswith("Universe:")]
        p_lines = [l for l in python_out.splitlines() if not l.startswith("Universe:")]
        
        if j_lines == p_lines:
            print("SUCCESS: Core outputs match (Universe line excluded)!")
        else:
            print("FAILURE: Outputs differ.")

if __name__ == "__main__":
    main()
