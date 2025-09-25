"""
Docker execution functionality for running user code in containers
"""

import docker
import tempfile
import os
import json
import yaml
from pathlib import Path
from .models import Result


def run_code_in_docker(user_code: str, kata_id: str) -> Result:
    """Execute user code in a secure Docker container"""

    # Find the kata YAML file
    kata_file = Path(f"katas/{kata_id.replace('-', '_')}.yaml")

    if not kata_file.exists():
        return Result(status="ERROR", message=f"Kata file not found: {kata_file}")

    try:
        # Load kata configuration
        with open(kata_file, 'r') as f:
            kata_config = yaml.safe_load(f)

        # Initialize Docker client
        try:
            client = docker.from_env()
            # Quick ping to ensure daemon reachable early
            client.ping()
        except docker.errors.DockerException as de:
            return Result(status="ERROR", message=f"Docker not available: {de}. Is the daemon running and do you have permission to access the Docker socket?")

# TODO Kind of ugly implementation .......  

        # Create a test runner script that tests the user code against YAML-defined test cases
        test_script = f'''
import json
import sys
import traceback

# Kata configuration
kata_config = {repr(kata_config)}

def test_solution(user_code: str) -> dict:
    """Test the user's solution against YAML-defined test cases"""
    try:
        # Execute user code to define the function
        exec_globals = {{}}
        exec(user_code, exec_globals)

        # Get the function name from kata config
        function_name = kata_config.get('function_name', 'solution')
        user_function = exec_globals.get(function_name)

        if not user_function:
            return {{
                "status": "ERROR",
                "message": f"Function '{{function_name}}' not found. Make sure you define a function named '{{function_name}}'."
            }}

        # Run test cases from YAML
        test_cases = kata_config.get('test_cases', [])

        for i, test_case in enumerate(test_cases):
            inputs = test_case.get('inputs', [])
            expected = test_case.get('expected')
            test_name = test_case.get('name', f"Test {{i+1}}")

            try:
                result = user_function(*inputs)
                if result != expected:
                    return {{
                        "status": "FAIL",
                        "message": f"{{test_name}} failed: {{function_name}}({{', '.join(map(str, inputs))}}) returned {{result}}, expected {{expected}}"
                    }}
            except Exception as e:
                return {{
                    "status": "ERROR",
                    "message": f"{{test_name}} failed with error: {{str(e)}}"
                }}

        return {{
            "status": "PASS",
            "message": "All tests passed! Great job!"
        }}

    except Exception as e:
        return {{
            "status": "ERROR",
            "message": f"Error executing code: {{str(e)}}"
        }}

# User submitted code
user_code = """
{user_code}
"""

def main():
    try:
        # Test the solution
        result = test_solution(user_code)
        print(json.dumps(result))
    except Exception as e:
        error_result = {{
            "status": "ERROR",
            "message": f"Error executing code: {{str(e)}}"
        }}
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()
'''

        # Create a temporary directory for the script
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "test_runner.py")
            with open(script_path, 'w') as f:
                f.write(test_script)

            # Run the container
            try:
                container = client.containers.run(
                    "python:3.11-alpine",
                    command=["python", "/app/test_runner.py"],
                    volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                    user="1000:1000",  # Non-root user
                    network_mode="none",  # No network access
                    mem_limit="128m",  # Memory limit
                    cpu_period=100000,
                    cpu_quota=50000,  # 50% CPU limit
                    remove=True,
                    stdout=True,
                    stderr=True
                )

                # Parse the JSON result
                output = container.decode('utf-8').strip()

                try:
                    result_data = json.loads(output)
                    return Result(
                        status=result_data["status"],
                        message=result_data["message"]
                    )
                except json.JSONDecodeError:
                    return Result(
                        status="ERROR",
                        message=f"Invalid output from container: {output}"
                    )

            except docker.errors.ContainerError as e:
                return Result(
                    status="ERROR",
                    message=f"Container execution failed: {e.stderr.decode() if e.stderr else str(e)}"
                )
            except Exception as e:
                return Result(
                    status="ERROR",
                    message=f"Docker execution error: {str(e)}"
                )

    except Exception as e:
        return Result(status="ERROR", message=f"Error setting up Docker execution: {str(e)}")