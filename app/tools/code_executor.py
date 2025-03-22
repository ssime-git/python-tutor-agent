# app/tools/code_executor.py
import json
import requests
from typing import Dict, Any
from langsmith import traceable

CODE_EXECUTOR_URL = "http://code-executor:8080/execute"

@traceable(name="execute_code_in_container")
def execute_code_in_container(code: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Execute Python code in a dedicated container and return the results.
    
    Args:
        code (str): Python code to execute
        timeout (int): Maximum execution time in seconds
        
    Returns:
        Dict with execution results
    """
    try:
        # Send code to the containerized execution service
        response = requests.post(
            CODE_EXECUTOR_URL,
            json={"code": code, "timeout": timeout},
            timeout=timeout + 2  # Slightly longer timeout for the HTTP request
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "output": "",
                "success": False,
                "error": f"Code execution service error: {response.status_code}",
                "execution_time": 0
            }
            
    except requests.exceptions.Timeout:
        return {
            "output": "",
            "success": False,
            "error": "Request to code execution service timed out",
            "execution_time": timeout
        }
        
    except Exception as e:
        return {
            "output": "",
            "success": False,
            "error": f"Error communicating with code execution service: {str(e)}",
            "execution_time": 0
        }