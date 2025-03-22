# Python Tutor Agent

A Python tutoring agent powered by LLMs that can answer Python programming questions and provide explanations.

## Architecture

The application consists of several components running in Docker containers:

1. **App Service**: A FastAPI application that handles user requests and serves as the main entry point.
   - Processes chat messages
   - Routes requests to the appropriate LLM service
   - Handles session management

2. **LiteLLM Proxy**: Serves as a gateway to various LLM providers.
   - Provides a unified API for different LLM models
   - Handles authentication and rate limiting
   - Currently configured to use Google's Gemini 2.0 Flash model

3. **Chroma**: Vector database for storing and retrieving embeddings.
   - Enables knowledge retrieval for answering specific questions
   - Supports semantic search capabilities

4. **Code Executor**: A service for executing Python code snippets.
   - Provides a safe environment for running user code
   - Returns execution results

### Architecture Diagram

```mermaid
graph TD
    User([User]) <--> A[App Service]
    A <--> B[LiteLLM Proxy]
    A <--> C[Chroma DB]
    A <--> D[Code Executor]
    B <--> E[Google Gemini API]
    
    subgraph Docker Environment
        A
        B
        C
        D
    end
    
    subgraph External Services
        E
    end
    
    classDef container fill:#d4f1f9,stroke:#333,stroke-width:1px;
    classDef external fill:#f9d6d2,stroke:#333,stroke-width:1px;
    classDef user fill:#d5f5d5,stroke:#333,stroke-width:1px;
    
    class A,B,C,D container;
    class E external;
    class User user;
```

## Features

The Python Tutor Agent offers a comprehensive set of features designed to provide an effective learning experience:

### Core Capabilities

- **Knowledge Retrieval**: Access to a rich database of Python concepts, best practices, and explanations
- **Code Execution**: Ability to run and analyze Python code in a secure environment
- **Intelligent Query Routing**: Automatic detection of whether a query requires knowledge retrieval or code execution
- **Structured Responses**: Clear, well-formatted responses with distinct sections for better understanding

### Enhanced Computation Handling

- **Mathematical Expression Detection**: Automatically identifies and processes mathematical expressions in queries
- **Natural Language to Code Conversion**: Translates phrases like "square root of 16" into executable Python code
- **Comprehensive Math Support**: Handles basic arithmetic, advanced operations, and mathematical functions
- **Smart Prioritization**: Correctly routes queries with both knowledge and computational elements

### Educational Features

- **Code Analysis**: Detailed breakdown of what code does and how it works
- **Error Explanation**: Clear explanations of errors and how to fix them
- **Best Practices**: Suggestions for code improvements and Python best practices
- **Related Concepts**: Links to related Python concepts for further learning

## Data Flow

1. User sends a message to the `/chat` endpoint
2. The app service processes the message and determines the appropriate action
3. For LLM requests, the app communicates with the LiteLLM proxy
4. The LiteLLM proxy forwards the request to the configured model (Gemini 2.0 Flash)
5. The response is returned to the user

## Requirements

- Docker and Docker Compose
- Google API Key for accessing Gemini models

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
GOOGLE_API_KEY=your_google_api_key_here
LITELLM_LOG_LEVEL=debug
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=python-tutor-agent
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### LiteLLM Configuration

The LiteLLM proxy is configured in `litellm-config/config.yaml`. The current configuration uses the Gemini 2.0 Flash model.

## Running the Application

1. Make sure Docker is installed and running
2. Set up the environment variables in a `.env` file
3. Start the application using Docker Compose:

```bash
docker compose up -d
```

4. Access the application at http://localhost:8000

## API Endpoints

- **POST /chat**: Send a message to the tutor agent
  - Request body: `{"message": "Your question about Python here"}`
  - Response: `{"response": "Agent's response", "session_id": "unique_session_id"}`

## Testing the Application

You can test the application using curl commands or any API client. Here are some examples:

### Testing Knowledge Retrieval

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do Python decorators work?"}'
```

### Testing Code Execution

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Please run this code: def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))"}'
```

### Testing Mathematical Expressions

```bash
# Testing simple arithmetic
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run the result of 1 + 1 in Python"}'

# Testing mathematical functions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the square root of 16 in Python?"}'

# Testing more complex calculations
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate the factorial of 5 in Python"}'
```

## Response Format

The agent provides structured responses with clear sections:

- **📘 Explanation** - Clear explanation of concepts or code
- **🔍 Code Analysis** - Detailed breakdown of what the code does
- **🚀 Execution Results** - Results of code execution (when applicable)
- **⚠️ Errors & Solutions** - Explanation of errors and how they were fixed
- **💡 Best Practices** - Tips and improvements for the code
- **🔗 Related Concepts** - Related Python concepts to explore

The responses use proper markdown formatting for improved readability.

## Intelligent Query Routing

The agent uses a sophisticated routing system to determine how to handle user queries:

### Code Execution Detection

The agent can intelligently detect when a query requires code execution, even if it's not explicitly requested:

- **Explicit Code Execution**: Detects phrases like "run this code", "execute this", etc.
- **Code Block Detection**: Automatically identifies Python code blocks in markdown format
- **Mathematical Expressions**: Recognizes and executes mathematical expressions and calculations
- **Simple Calculations**: Handles queries like "run the result of 1 + 1 in Python" or "what is the square root of 16 in Python"

### Mathematical Operations Support

The agent can detect and execute a wide range of mathematical operations:

- Basic arithmetic (addition, subtraction, multiplication, division)
- Advanced operations (exponentiation, square roots, logarithms)
- Mathematical functions (trigonometric functions, statistical calculations)
- Python's built-in math module functions

### Intelligent Expression Extraction

When a mathematical expression is detected:

1. The agent extracts the expression from the user's query
2. Converts natural language (e.g., "square root of 16") to valid Python code (e.g., `math.sqrt(16)`)
3. Executes the code and provides the result along with an educational explanation

### Knowledge vs. Computation Prioritization

The agent intelligently prioritizes:
- Code execution for computational queries, even if they contain knowledge-seeking keywords
- Knowledge retrieval for conceptual questions without computational elements

## Monitoring and Debugging

### Logging

The application includes comprehensive logging to help with debugging and monitoring. Logs are output to the console and include timestamps, log levels, and detailed information about the agent's operations.

### LangSmith Integration

The agent is integrated with LangSmith for tracing and monitoring. To use LangSmith:

1. Create an account at [LangSmith](https://smith.langchain.com/)
2. Get your API key from the LangSmith dashboard
3. Copy `.env.example` to `.env` and add your LangSmith API key:
   ```
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   ```
4. Restart the application

Once configured, you can view traces, monitor performance, and debug your agent in the LangSmith dashboard.

## Recent Updates

### Code Execution Improvements

The code execution functionality has been improved to:
- Extract Python code directly from user messages using regex pattern matching
- Properly handle markdown code blocks (```python ... ```)
- Fall back to LLM extraction only when regex fails
- Ensure the `/tmp/executions` directory exists and has proper permissions in the code-executor container

### ChromaDB Integration

The application now uses the ChromaDB service instead of a local Chroma instance:
- Connects to the ChromaDB service running at http://chroma:8000
- Creates and manages collections for storing Python knowledge
- Provides fallback to in-memory Chroma if the service is unavailable
- Compatible with ChromaDB v0.6.0 API

### Enhanced Routing Logic

The agent's routing logic has been improved to:
- Detect mathematical expressions and calculations in user queries
- Convert natural language math descriptions into executable Python code
- Prioritize code execution when both knowledge retrieval and math are detected
- Handle a wide range of mathematical operations including arithmetic, advanced operations, and functions
- Extract and execute simple expressions like "1 + 1" or complex ones like "square root of 16"

## Development

To modify the application:

1. Update the code in the `app` directory
2. Rebuild and restart the containers:
   ```bash
   docker compose down && docker compose up --build -d
   ```

## Troubleshooting

- If you encounter issues with the LiteLLM service, check the logs:
  ```bash
  docker compose logs litellm
  ```

- To check the ChromaDB service logs:
  ```bash
  docker compose logs chroma
  ```

- To check the code executor service logs:
  ```bash
  docker compose logs code-executor
  ```

- To restart all services:
  ```bash
  docker compose down && docker compose up -d
  ```

## Agent Logic

The Python Tutor Agent follows a structured decision-making process to handle user queries effectively:

### Query Processing Flow

```mermaid
flowchart TD
    A[User Query] --> B{Route Query}
    
    %% Decision Logic
    B -->|Code Detected| C[Code Execution Path]
    B -->|Knowledge Request| D[Knowledge Retrieval Path]
    
    %% Code Execution Branch
    C --> C1[Extract Code/Math Expression]
    C1 --> C2[Format for Execution]
    C2 --> C3[Execute in Container]
    C3 --> C4[Capture Results/Errors]
    C4 --> C5{Errors?}
    C5 -->|Yes| C6[Attempt Auto-Fix]
    C5 -->|No| E[Response Generation]
    C6 --> E
    
    %% Knowledge Retrieval Branch
    D --> D1[Search Vector Database]
    D1 --> D2[Retrieve Relevant Content]
    D2 --> E
    
    %% Response Generation
    E --> E1[Format with Educational Context]
    E1 --> E2[Structure Response with Markdown]
    E2 --> F[Return to User]
    
    %% Decision Logic Details
    subgraph "Routing Decision Logic"
        G[Query Analysis]
        G --> G1{Contains Code Block?}
        G1 -->|Yes| C
        G1 -->|No| G2{Math Expression?}
        G2 -->|Yes| C
        G2 -->|No| G3{Explicit Code Request?}
        G3 -->|Yes| C
        G3 -->|No| G4{Knowledge Request?}
        G4 -->|Yes| D
        G4 -->|No| G5[Ask for Clarification]
    end
    
    %% Styling
    classDef process fill:#d4f1f9,stroke:#333,stroke-width:1px;
    classDef decision fill:#ffe6cc,stroke:#333,stroke-width:1px;
    classDef output fill:#d5f5d5,stroke:#333,stroke-width:1px;
    
    class A,C1,C2,C3,C4,C6,D1,D2,E1,E2,G process;
    class B,C5,G1,G2,G3,G4 decision;
    class F,G5 output;
```

### Decision Logic

```mermaid
flowchart TD
    Start([User Query]) --> A{Explicit Code Request?}
    A -->|Yes| Z[Execute Code]
    A -->|No| B{Contains Code Block?}
    
    B -->|Yes| Z
    B -->|No| C{Contains Math Expression?}
    
    C -->|Yes| Z
    C -->|No| D{Knowledge Request?}
    
    D -->|Yes| Y[Retrieve Knowledge]
    D -->|No| E{Query Length > 3 Words?}
    
    E -->|Yes| Y
    E -->|No| X[Ask for Clarification]
    
    %% Priority for Mixed Queries
    F[Mixed Query\nKnowledge + Math] --> G{Math Detected?}
    G -->|Yes| Z
    G -->|No| Y
    
    %% Styling
    classDef process fill:#d4f1f9,stroke:#333,stroke-width:1px;
    classDef decision fill:#ffe6cc,stroke:#333,stroke-width:1px;
    classDef output fill:#d5f5d5,stroke:#333,stroke-width:1px;
    
    class Start process;
    class A,B,C,D,E,G decision;
    class X,Y,Z output;
```

For mixed queries (containing both knowledge and computational elements), the agent prioritizes code execution when mathematical operations are detected.

## Potential Improvements

Future enhancements to the Python Tutor Agent could include:

### Functionality Improvements

1. **Multi-turn Conversations**: Enhance the agent to maintain context across multiple interactions, allowing for follow-up questions and progressive learning.

2. **Code Visualization**: Integrate with tools like Python Tutor's visualization engine to provide step-by-step visual execution of code.

3. **Interactive Code Exercises**: Generate practice exercises based on the concepts being discussed and provide feedback on user solutions.

4. **Personalized Learning Paths**: Track user interactions to identify knowledge gaps and suggest personalized learning resources.

5. **Advanced Error Analysis**: Provide more detailed explanations of common Python errors with visual indicators of where the error occurred.

### Technical Improvements

1. **Performance Optimization**: Improve response times by optimizing the code extraction and execution processes.

2. **Model Enhancements**: Experiment with different LLM models to find the optimal balance between performance and accuracy.

3. **Knowledge Base Expansion**: Continuously update and expand the knowledge base with the latest Python features and best practices.

4. **Enhanced Security**: Implement additional security measures for the code execution environment to prevent potential exploits.

5. **Offline Mode**: Add support for running the agent locally without internet connectivity for educational environments with limited access.

### UI/UX Improvements

1. **Mobile Responsiveness**: Optimize the frontend for better mobile device support.

2. **Dark Mode**: Add a dark mode option for reduced eye strain during extended use.

3. **Code Editor Integration**: Provide a built-in code editor with syntax highlighting for easier code entry.

4. **Result History**: Allow users to save and revisit previous interactions and code executions.

5. **Export Functionality**: Enable exporting of conversations and code examples for reference.

## Contributing

Contributions to the Python Tutor Agent are welcome! Please feel free to submit issues or pull requests to help improve the project.