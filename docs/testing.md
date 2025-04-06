Great! Now that the LLMOps architecture is running, let's test it to ensure everything is working properly.

## Testing Your LLMOps Architecture

### 1. Basic Web Interface Test

First, let's verify that the web interface is accessible:

1. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

2. You should see the chat interface with a welcome message from the Python Mentor Agent.

### 2. Testing Core Functionality

Let's test each of the core capabilities:

#### Test the Direct Response Capability
Type a simple query that doesn't require code execution or knowledge retrieval:

```sh
What is Python used for?
```

#### Test the Knowledge Retrieval Capability
Ask a question about Python concepts:
```
How do Python decorators work?
```

#### Test the Code Execution Capability
Ask the agent to write and run some code:
```
Can you write a Python function to find prime numbers up to 50?
```

#### Test Error Handling
Submit code with a deliberate error to see how the system handles it:
```
Can you fix this code: for i in range(10) print(i)
```

### 3. Testing the Isolated Code Execution Container

To verify that code execution is happening in the isolated container:

1. Ask the agent to execute a file system operation:
   ```
   Can you write code to list files in the current directory?
   ```

2. Try to access restricted resources:
   ```
   Can you write code to show system memory usage?
   ```

### 4. Checking LangSmith Tracing

If you've set up LangSmith with your API key:

1. Go to the LangSmith dashboard:
   ```
   https://smith.langchain.com/
   ```

2. Look for your project (named "llmops-demo" in the configuration)

3. You should see traces for your interactions, showing each step of the agent's reasoning process

### 5. Testing LiteLLM Model Use

To verify that your system is using LiteLLM with Gemini Flash:

1. Ask a complex question that requires significant reasoning:
   ```
   What's the difference between shallow copy and deep copy in Python? Can you explain with examples?
   ```

2. Check the logs to confirm the model being used:
   ```bash
   docker-compose logs app | grep "model"
   ```

### 6. Debugging Tips

If you encounter any issues:

1. Check Docker container logs:
   ```bash
   docker-compose logs
   ```

2. For specific service logs:
   ```bash
   docker-compose logs app
   docker-compose logs code-executor
   docker-compose logs chroma
   ```

3. Connect to the app container to investigate:
   ```bash
   docker-compose exec app bash
   ```

### 7. Testing Chroma Vector Store

To verify the vector store is working:

1. Ask multiple related questions about the same topic to see if the responses improve as the context builds:
   ```
   What are Python list comprehensions?
   ```
   
   Followed by:
   ```
   Can you show me some advanced examples of list comprehensions?
   ```

### 8. Testing Error Resilience

1. Try to deliberately crash the code executor with an infinite loop:
   ```
   Can you run this code: while True: pass
   ```
   
   The system should terminate the execution after the timeout period.

If all these tests work successfully, your LLMOps architecture is functioning as expected! Let me know if you encounter any specific issues or if you'd like to test additional features.

# Python Tutor Agent Testing Guide

This document contains a comprehensive set of test cases for the Python Tutor Agent. Use these examples to verify that the agent is working correctly.

## Knowledge Retrieval Tests

Test the agent's ability to retrieve Python knowledge by asking questions about Python concepts.

### Basic Python Concepts

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python and what are its main features?"}'
```

### Python Variables

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do variables work in Python?"}'
```

### Python Functions

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Python functions and their parameters"}'
```

### Python Decorators

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do Python decorators work?"}'
```

### Python Dictionaries

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are Python dictionaries and how do they work?"}'
```

### Python Classes and OOP

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Python classes and object-oriented programming"}'
```

### Python Exceptions

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does exception handling work in Python?"}'
```

## Code Execution Tests

Test the agent's ability to execute Python code and provide explanations.

### Simple Calculation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\nx = 10\ny = 5\nprint(f\"Sum: {x + y}\")\nprint(f\"Difference: {x - y}\")\nprint(f\"Product: {x * y}\")\nprint(f\"Quotient: {x / y}\")\n```"}'
```

### List Manipulation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\nnumbers = [1, 2, 3, 4, 5]\nprint(\"Original list:\", numbers)\n\n# Add elements\nnumbers.append(6)\nprint(\"After append:\", numbers)\n\n# Insert at specific position\nnumbers.insert(0, 0)\nprint(\"After insert:\", numbers)\n\n# Remove element\nnumbers.remove(3)\nprint(\"After remove:\", numbers)\n\n# List comprehension\nsquares = [x**2 for x in numbers]\nprint(\"Squares:\", squares)\n```"}'
```

### Dictionary Operations

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\n# Create a dictionary\nstudent = {\n    \"name\": \"John\",\n    \"age\": 21,\n    \"courses\": [\"Math\", \"Physics\", \"Computer Science\"]\n}\n\nprint(\"Original dictionary:\", student)\n\n# Access values\nprint(\"Name:\", student[\"name\"])\nprint(\"Age:\", student[\"age\"])\nprint(\"Courses:\", student[\"courses\"])\n\n# Add new key-value pair\nstudent[\"grade\"] = \"A\"\nprint(\"After adding grade:\", student)\n\n# Update value\nstudent[\"age\"] = 22\nprint(\"After updating age:\", student)\n\n# Remove key-value pair\ndel student[\"courses\"]\nprint(\"After deleting courses:\", student)\n```"}'
```

### Class Definition and Usage

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\nclass Calculator:\n    def __init__(self):\n        self.result = 0\n    \n    def add(self, num):\n        self.result += num\n        return self\n    \n    def subtract(self, num):\n        self.result -= num\n        return self\n    \n    def multiply(self, num):\n        self.result *= num\n        return self\n    \n    def divide(self, num):\n        if num == 0:\n            raise ValueError(\"Cannot divide by zero\")\n        self.result /= num\n        return self\n    \n    def get_result(self):\n        return self.result\n\n# Test the calculator\ncalc = Calculator()\ncalc.add(10).subtract(5).multiply(2).divide(5)\nprint(f\"Result: {calc.get_result()}\")  # Should print 2.0\n\n# Test error handling\ntry:\n    calc.divide(0)\nexcept ValueError as e:\n    print(f\"Error caught: {e}\")\n```"}'
```

### Exception Handling

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\ndef divide(a, b):\n    try:\n        result = a / b\n        print(f\"{a} / {b} = {result}\")\n    except ZeroDivisionError:\n        print(\"Error: Cannot divide by zero\")\n    except TypeError:\n        print(\"Error: Invalid types for division\")\n    else:\n        print(\"Division successful!\")\n    finally:\n        print(\"This always executes\")\n\nprint(\"Test case 1: Valid division\")\ndivide(10, 2)\n\nprint(\"\\nTest case 2: Division by zero\")\ndivide(10, 0)\n\nprint(\"\\nTest case 3: Invalid types\")\ndivide(\"10\", 2)\n```"}'
```

### Recursive Function

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\ndef factorial(n):\n    \"\"\"Calculate the factorial of a number recursively\"\"\"\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)\n\n# Test the factorial function\nfor i in range(6):\n    print(f\"{i}! = {factorial(i)}\")\n\n# Calculate factorial of 10\nresult = factorial(10)\nprint(f\"10! = {result}\")\n```"}'
```

### File Operations (Note: This will only work if the container has write access)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code: \n\n```python\nimport os\n\n# Create a temporary file\nfilename = \"/tmp/executions/test_file.txt\"\n\n# Write to file\nwith open(filename, \"w\") as f:\n    f.write(\"Line 1: Hello, World!\\n\")\n    f.write(\"Line 2: Python file operations\\n\")\n    f.write(\"Line 3: Testing file I/O\")\n\nprint(f\"File created: {filename}\")\n\n# Read from file\nprint(\"\\nReading file contents:\")\nwith open(filename, \"r\") as f:\n    contents = f.read()\n    print(contents)\n\n# Read line by line\nprint(\"\\nReading line by line:\")\nwith open(filename, \"r\") as f:\n    for i, line in enumerate(f, 1):\n        print(f\"Line {i}: {line.strip()}\")\n\n# Append to file\nwith open(filename, \"a\") as f:\n    f.write(\"\\nLine 4: Appended line\")\n\nprint(\"\\nAfter appending:\")\nwith open(filename, \"r\") as f:\n    print(f.read())\n\n# Clean up\nos.remove(filename)\nprint(f\"\\nFile {filename} removed\")\n```"}'
```

## Combined Knowledge and Code Tests

Test the agent's ability to both explain concepts and execute related code.

### List Comprehension

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain list comprehensions in Python and then run this example: \n\n```python\n# Basic list comprehension\nnumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\neven_squares = [x**2 for x in numbers if x % 2 == 0]\nprint(f\"Even squares: {even_squares}\")\n\n# Nested list comprehension\nmatrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\ntransposed = [[row[i] for row in matrix] for i in range(3)]\nprint(f\"Original matrix: {matrix}\")\nprint(f\"Transposed matrix: {transposed}\")\n```"}'
```

### Decorator Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Python decorators and then run this example: \n\n```python\nimport time\n\ndef timing_decorator(func):\n    def wrapper(*args, **kwargs):\n        start_time = time.time()\n        result = func(*args, **kwargs)\n        end_time = time.time()\n        print(f\"Function {func.__name__} took {end_time - start_time:.6f} seconds to run\")\n        return result\n    return wrapper\n\n@timing_decorator\ndef calculate_sum(n):\n    return sum(range(n))\n\n@timing_decorator\ndef calculate_squares(n):\n    return [x**2 for x in range(n)]\n\nprint(f\"Sum of first 1,000,000 numbers: {calculate_sum(1000000)}\")\nprint(f\"Squares of first 10,000 numbers: {len(calculate_squares(10000))} items calculated\")\n```"}'
```

## Error Cases

Test how the agent handles error cases.

### Syntax Error

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code with a syntax error: \n\n```python\nprint(\"This line is fine\")\nif True\n    print(\"This line has a syntax error - missing colon\")\nprint(\"This line will not be reached due to the error\")\n```"}'
```

### Runtime Error

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code with a runtime error: \n\n```python\nprint(\"This line is fine\")\nx = 10 / 0  # Division by zero error\nprint(\"This line will not be reached due to the error\")\n```"}'
```

### Infinite Loop (should be caught by timeout)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code with an infinite loop: \n\n```python\nprint(\"Starting infinite loop - should be caught by timeout\")\nwhile True:\n    pass  # Infinite loop\nprint(\"This line will never be reached\")\n```"}'
```

## Performance Testing

Test the agent's performance with more complex code.

### Fibonacci Sequence

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code to calculate Fibonacci numbers: \n\n```python\ndef fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number\"\"\"\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n\n# Calculate and print the first 20 Fibonacci numbers\nprint(\"First 20 Fibonacci numbers:\")\nfor i in range(20):\n    print(f\"fibonacci({i}) = {fibonacci(i)}\")\n```"}'
```

### Prime Number Generator

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run this Python code to generate prime numbers: \n\n```python\ndef is_prime(n):\n    \"\"\"Check if a number is prime\"\"\"\n    if n <= 1:\n        return False\n    if n <= 3:\n        return True\n    if n % 2 == 0 or n % 3 == 0:\n        return False\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0:\n            return False\n        i += 6\n    return True\n\ndef generate_primes(limit):\n    \"\"\"Generate prime numbers up to the given limit\"\"\"\n    primes = []\n    for num in range(2, limit + 1):\n        if is_prime(num):\n            primes.append(num)\n    return primes\n\n# Generate primes up to 100\nprimes = generate_primes(100)\nprint(f\"Prime numbers up to 100: {primes}\")\nprint(f\"Total count: {len(primes)}\")\n```"}'
```

## Troubleshooting

If you encounter issues with any of these tests, check the logs of the relevant services:

```bash
# Check app logs
docker compose logs app

# Check code executor logs
docker compose logs code-executor

# Check ChromaDB logs
docker compose logs chroma

# Check LiteLLM logs
docker compose logs litellm
```

To restart all services:

```bash
docker compose down && docker compose up -d