"""
Sandbox runner for executing Python scripts using nsjail in WSL
"""

import subprocess
import os


def run_script(script_path, stdin_input="", timeout=2, memory_limit=512, 
               max_cpus=1, allow_network=False, max_file_size=1):
    """
    Run a Python script in nsjail sandbox via WSL.
    
    Args:
        script_path: Path to Python script (Windows path or filename)
        stdin_input: Input to pass via stdin
        timeout: Max execution time in seconds (default: 2)
        memory_limit: Max memory in MB (default: 512)
        max_cpus: Max number of CPUs the process can use (default: 1)
        allow_network: Whether to allow network access (default: False)
        max_file_size: Max file size that can be created in MB (default: 1)
        
    Returns:
        dict with: returncode, stdout, stderr, success
    """
    # Convert Windows path to WSL path
    abs_path = os.path.abspath(script_path)
    drive = abs_path[0].lower()
    wsl_source = f"/mnt/{drive}{abs_path[2:].replace(chr(92), '/')}"
    
    # Copy to WSL /tmp (nsjail has issues with /mnt paths)
    wsl_temp = f"/tmp/{os.path.basename(script_path)}"
    copy_cmd = ["wsl", "cp", wsl_source, wsl_temp]
    subprocess.run(copy_cmd, capture_output=True)
    
    # Build nsjail command
    cmd = [
        "wsl", "-e", "sudo", "/usr/local/sbin/nsjail",
        "-Mo", 
        "-t", str(timeout),
        "--disable_clone_newuser",
        "-R", "/usr",
        "-R", "/lib", "-R", "/lib64",
        "-R", "/etc", "-R", "/dev/null",
        "--cwd", "/app",
        "-R", f"{wsl_temp}:/app/script.py",
        "--rlimit_as", str(memory_limit),  # Memory limit
        "--rlimit_cpu", str(timeout),  # CPU time limit
        "--rlimit_fsize", str(max_file_size),  # Max file size
        "--max_cpus", str(max_cpus),  # CPU count limit
    ]
    
    # Network isolation
    if not allow_network:
        cmd.append("--disable_clone_newnet")
    
    # Python execution
    cmd.extend(["--", "/usr/bin/python3", "-I", "-B", "/app/script.py"])
    
    try:
        result = subprocess.run(
            cmd,
            input=stdin_input,
            text=True,
            capture_output=True,
            timeout=timeout + 2
        )
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Timeout after {timeout}s",
            "success": False
        }
    
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }
    
    finally:
        # Clean up temp file
        subprocess.run(["wsl", "rm", "-f", wsl_temp], capture_output=True)


# Example usage
if __name__ == "__main__":
    # Test 1: Basic execution
    with open("test.py", 'w') as f:
        f.write("print('Hello from sandbox!')")
    
    result = run_script("test.py")
    print("Test 1 - Basic:")
    print("Return code:", result['returncode'])
    print("Output:", result['stdout'])
    print()
    
    # Test 2: With custom timeout
    with open("test.py", 'w') as f:
        f.write("import time; time.sleep(1); print('Finished')")
    
    result = run_script("test.py", timeout=3)
    print("Test 2 - Custom timeout:")
    print("Return code:", result['returncode'])
    print("Output:", result['stdout'])
    print()
    
    # Test 3: With memory limit
    result = run_script("test.py", memory_limit=256)
    print("Test 3 - Memory limit:")
    print("Return code:", result['returncode'])
    print()
    
    os.unlink("test.py")
