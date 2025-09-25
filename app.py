"""
Simple Kata Execution Platform

A minimal FastAPI application for running Python coding challenges.
Users submit code via web interface, code runs in Docker containers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List

from models import Kata, Submission, Result
from kata_manager import KATAS
from docker_executor import run_code_in_docker

app = FastAPI(title="Simple Kata Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)