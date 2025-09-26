# Py-Katas: Simple Kata Exercise

A web-based interface to execute kata validation code using Docker and FastAPI. Executes user code in an isolated containers.

## Architecture

```
Browser (HTML/JS) → FastAPI Server → Docker Container
                                   ↓
                               Python Code Execution
                                   ↓
                               PASS/FAIL Result
```

## Components

- **Frontend**: Simple HTML/JS interface for submitting code and viewing results (Vanilla JS,).
- **Backend**: FastAPI server handling requests and managing Docker containers.
- **Docker**: Isolated environment for secure code execution.


## To Do (Move this to git hub issues)
- Refactor the fastApi code so it is not all in one file. docker and kata management should be in separate files.
- Implement not blocking docker execution. Right now the server is blocked until the docker container finishes. Should be an async call.
- Can it handle multiple requests at the same time? What about 1000 requests? 
- A way to warm up the docker containers so they start faster.
- Should add tests for the API endpoints.
- How could we scale this? K8s?

## Setup
    
1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd py-katas
   ```

2. Set up a Python virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python start.py
   ```