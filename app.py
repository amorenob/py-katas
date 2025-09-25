"""
Simple Kata Execution Platform

A minimal FastAPI application for running Python coding challenges.
Users submit code via web interface, code runs in Docker containers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import docker
import tempfile
import os
import json
import importlib.util
import sys
from pathlib import Path
from typing import List

app = FastAPI(title="Simple Kata Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data models
class Kata(BaseModel):
    id: str
    title: str
    description: str
    starter_code: str

class Submission(BaseModel):
    kata_id: str
    code: str

class Result(BaseModel):
    status: str  # "PASS", "FAIL", or "ERROR"
    message: str = ""

def load_katas():
    """Load katas from the katas directory"""
    katas = []
    katas_dir = Path("katas")
    
    if not katas_dir.exists():
        return katas
        
    for kata_file in katas_dir.glob("*.py"):
        try:
            # Import the kata module
            spec = importlib.util.spec_from_file_location(kata_file.stem, kata_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get kata info
                if hasattr(module, 'kata_info'):
                    info = module.kata_info()
                    kata = Kata(**info)
                    katas.append(kata)
                    
        except Exception as e:
            print(f"Error loading kata {kata_file}: {e}")
            
    return katas

# Load available katas
KATAS = load_katas()

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(f.read())

@app.get("/katas", response_model=List[Kata])
async def list_katas():
    """Get all available katas"""
    return KATAS

@app.get("/katas/{kata_id}", response_model=Kata) 
async def get_kata(kata_id: str):
    """Get details for a specific kata"""
    for kata in KATAS:
        if kata.id == kata_id:
            return kata
    raise HTTPException(status_code=404, detail="Kata not found")

@app.post("/submit", response_model=Result)
async def submit_solution(submission: Submission):
    """Submit code solution and get result"""
    
    # Find the kata
    kata = None
    for k in KATAS:
        if k.id == submission.kata_id:
            kata = k
            break
    
    if not kata:
        raise HTTPException(status_code=404, detail="Kata not found")
    
    # Run code in Docker container
    try:
        result = run_code_in_docker(submission.code, submission.kata_id)
        return result
    except Exception as e:
        return Result(status="ERROR", message=str(e))

def run_code_in_docker(user_code: str, kata_id: str) -> Result:
    """Execute user code in a secure Docker container"""
    
    # Find the kata file
    kata_file = Path(f"katas/{kata_id.replace('-', '_')}.py")
    
    if not kata_file.exists():
        return Result(status="ERROR", message=f"Kata file not found: {kata_file}")
    
    try:
        # Initialize Docker client
        try:
            client = docker.from_env()
            # Quick ping to ensure daemon reachable early
            client.ping()
        except docker.errors.DockerException as de:
            return Result(status="ERROR", message=f"Docker not available: {de}. Is the daemon running and do you have permission to access the Docker socket?")
        
        # Read the kata file content
        with open(kata_file, 'r') as f:
            kata_content = f.read()
        
        # Create a test runner script that combines kata and user code
        test_script = f'''
import json
import sys
import traceback

# Kata module content
{kata_content}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)