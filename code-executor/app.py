# code-executor/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import signal
import time
from typing import Dict, Any, Optional

app = FastAPI(title="Code Execution Sandbox")

class CodeRequest(BaseModel):
    code: str
    timeout: Optional[int] = 5  # Default timeout in seconds

class CodeResponse(BaseModel):
    output: str
    success: bool
    error: Optional[str] = None
    execution_time: float

@app.post("/execute", response_model=CodeResponse)
async def execute_code(request: CodeRequest) -> Dict[str, Any]:
    """Execute provided code in a sandboxed environment"""
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, dir="/tmp/executions") as temp_file:
        temp_file.write(request.code.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        start_time = time.time()
        
        # Run the code in a subprocess with restricted permissions
        process = subprocess.Popen(
            ["python", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Create a new process group for easier termination
        )
        
        try:
            # Wait for completion with timeout
            stdout, stderr = process.communicate(timeout=request.timeout)
            execution_time = time.time() - start_time
            
            if process.returncode == 0:
                return {
                    "output": stdout,
                    "success": True,
                    "execution_time": execution_time
                }
            else:
                return {
                    "output": "",
                    "success": False,
                    "error": stderr,
                    "execution_time": execution_time
                }
                
        except subprocess.TimeoutExpired:
            # Kill the process group if timeout occurs
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.kill()
            return {
                "output": "",
                "success": False,
                "error": f"Execution timed out after {request.timeout} seconds",
                "execution_time": request.timeout
            }
            
    except Exception as e:
        return {
            "output": "",
            "success": False,
            "error": str(e),
            "execution_time": 0
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}