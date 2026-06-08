import subprocess
import os
import sys
from typing import Dict, Any

def execute_python_code(code: str, workspace_dir: str) -> Dict[str, Any]:
    """
    Writes Python code to a file and executes it in a sandboxed subprocess.
    Returns stdout, stderr, and the return code.
    """
    os.makedirs(workspace_dir, exist_ok=True)
    script_path = os.path.join(workspace_dir, "experiment.py")
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)
        
    try:
        # Run using the current python executable to ensure same virtualenv packages are available
        result = subprocess.run(
            [sys.executable, os.path.abspath(script_path)],
            cwd=workspace_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired as e:
        # Retrieve stdout and stderr if any was captured before timeout
        stdout = e.stdout.decode('utf-8', errors='ignore') if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode('utf-8', errors='ignore') if isinstance(e.stderr, bytes) else (e.stderr or "")
        return {
            "stdout": stdout,
            "stderr": stderr + "\n[ERROR: Script execution timed out after 20 seconds]",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"[ERROR: Exception occurred during sandbox run: {str(e)}]",
            "exit_code": -1
        }

if __name__ == "__main__":
    test_code = "print('Hello from Sandbox!')\nimport sys\nprint('Python:', sys.version)"
    print(execute_python_code(test_code, "./run_env_test"))
