# Python Tutor Agent Test Cases

This document contains various test cases to demonstrate the Python Tutor Agent's capabilities, particularly focusing on the enhanced routing logic and code execution features.

## Basic Knowledge Retrieval

Test the agent's ability to retrieve knowledge about Python concepts:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do Python decorators work?"}'
```

## Code Execution

Test the agent's ability to execute Python code:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Please run this code: def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))"}'
```

## Mathematical Expressions

### Simple Arithmetic

Test the agent's ability to handle simple arithmetic expressions:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run the result of 1 + 1 in Python"}'
```

Expected behavior: The agent should detect this as a code execution request, extract the expression "1 + 1", and execute it.

### Mathematical Functions

Test the agent's ability to handle mathematical functions:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the square root of 16 in Python?"}'
```

Expected behavior: Despite containing "what is" (typically a knowledge retrieval trigger), the agent should prioritize code execution due to the mathematical nature of the query, convert "square root of 16" to `math.sqrt(16)`, and execute it.

### Complex Calculations

Test the agent's ability to handle more complex calculations:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate the factorial of 5 in Python"}'
```

Expected behavior: The agent should detect this as a code execution request, understand that it needs to calculate a factorial, and execute the appropriate code.

## Mixed Queries

Test the agent's ability to handle queries that contain both knowledge retrieval and code execution elements:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain how to calculate the area of a circle with radius 5 in Python"}'
```

Expected behavior: The agent should prioritize code execution due to the calculation aspect, while also providing an explanation of the concept.

## Edge Cases

### Implicit Code Execution

Test the agent's ability to detect implicit code execution requests:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "5 * 10 + 2"}'
```

Expected behavior: The agent should recognize this as a mathematical expression and execute it, even though there's no explicit request to do so.

### Mathematical Terms in Natural Language

Test the agent's ability to handle mathematical terms in natural language:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the result when you find the square root of 25 and then add 3 to it?"}'
```

Expected behavior: The agent should extract the mathematical operations, convert them to code, and execute them.
