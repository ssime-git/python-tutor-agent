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

### Data Flow

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

## Response Format

The agent provides structured responses with clear sections:

- **📘 Explanation** - Clear explanation of concepts or code
- **🔍 Code Analysis** - Detailed breakdown of what the code does
- **🚀 Execution Results** - Results of code execution (when applicable)
- **⚠️ Errors & Solutions** - Explanation of errors and how they were fixed
- **💡 Best Practices** - Tips and improvements for the code
- **🔗 Related Concepts** - Related Python concepts to explore

The responses use proper markdown formatting for improved readability.

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

## Development

To modify the application:

1. Update the code in the `app` directory
2. Rebuild and restart the containers:
   ```bash
   docker compose down && docker compose up --build -d
   ```