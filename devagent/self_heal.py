import subprocess
import os

def check_for_errors(entry_point: str) -> tuple[bool, str]:
    """Run a Python file and check for errors. Return (has_error, error_msg)."""
    if not entry_point.endswith(".py"):
        return True, f"Error: Entry point '{entry_point}' must be a Python (.py) file."
    
    if not os.path.exists(entry_point):
        return True, f"Error: File '{entry_point}' not found."
    
    try:
        # Run the file and capture output/errors
        result = subprocess.run(
            ["python", entry_point],
            capture_output=True,
            text=True,
            timeout=30 # Adjust timeout as needed
        )
        
        if result.returncode == 0:
            return False, result.stdout
        else:
            return True, f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return True, "Error: Execution timed out (potential infinite loop or long-running process)."
    except Exception as e:
        return True, f"Error: Could not execute '{entry_point}': {str(e)}"
