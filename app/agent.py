import os
import json
import requests
import time
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from langsmith import traceable
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from tools.code_executor import execute_code_in_container
from tools.retriever import setup_chroma_retriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)
logger = logging.getLogger("python-tutor-agent")

# Configure LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "python-tutor-agent"
if not os.environ.get("LANGCHAIN_ENDPOINT"):
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
logger.info(f"LangSmith tracing enabled for project: {os.environ.get('LANGCHAIN_PROJECT')}")

# Initialize vector retriever
retriever = setup_chroma_retriever()

# Define message type
class Message(TypedDict):
    role: str
    content: str

# Define state as a TypedDict for newer LangGraph compatibility
class AgentState(TypedDict):
    messages: List[Message]
    next_step: str
    context: Dict[str, Any]

# Get LLM
def get_llm(temperature=0.2):
    """Get a direct LLM instance"""
    logger.info("Getting LLM instance")
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=temperature,
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )

# Define a direct LLM call function
def call_llm(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """Call LLM via local LiteLLM server with fallback to direct API"""
    logger.info("Calling LLM")
    # Try the LiteLLM service first
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://litellm:4000/v1/chat/completions",
                json={
                    "model": "gemini/gemini-2.0-flash",  # Use the full model name in the format expected by LiteLLM
                    "messages": messages,
                    "temperature": temperature
                },
                headers={
                    "Content-Type": "application/json",
                    # Uncomment and use if you set a master key in config.yaml
                    # "Authorization": f"Bearer {os.environ.get('LITELLM_MASTER_KEY', '')}"
                },
                timeout=30  # Longer timeout
            )
            
            if response.status_code == 200:
                logger.info("Using LiteLLM service")
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"LiteLLM error (attempt {attempt+1}/{max_retries}): {response.status_code}")
                logger.error(f"Response content: {response.text}")
                if attempt == max_retries - 1:
                    # Last attempt, fall back to direct API
                    raise Exception(f"LiteLLM error after {max_retries} attempts: {response.text}")
                # Wait before retrying
                time.sleep(2)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"All LiteLLM attempts failed, using direct API: {e}")
                # Fall back to direct API call on the last attempt
                llm = get_llm(temperature)
                response = llm.invoke([{"role": m["role"], "content": m["content"]} for m in messages])
                return response.content
            logger.error(f"LiteLLM attempt {attempt+1} failed: {e}")
            time.sleep(2)  # Wait before retry
    
    # If we get here, all retries failed
    llm = get_llm(temperature)
    response = llm.invoke([{"role": m["role"], "content": m["content"]} for m in messages])
    return response.content

# Router function
@traceable(name="route_query")
def route_query(state: AgentState) -> AgentState:
    """Determine the next step based on the user query"""
    logger.info("Routing query")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    
    # Initialize context if not present
    if "context" not in state:
        state["context"] = {}
    
    # Check for code execution request
    code_execution_keywords = [
        "run this code", "execute this", "run the following", 
        "execute the following", "run this program", "execute this program",
        "can you run", "please run", "can you execute", "please execute"
    ]
    
    # Check for specific code execution request
    is_execution_request = any(keyword.lower() in user_message.lower() for keyword in code_execution_keywords)
    
    # Check for code presence (even without explicit execution request)
    code_indicators = ["```python", "```", "def ", "class ", "import ", "print("]
    has_code = any(indicator in user_message for indicator in code_indicators)
    
    # Check for knowledge retrieval keywords
    knowledge_keywords = [
        "explain", "what is", "how does", "tell me about", "describe",
        "what are", "how do", "why is", "when should", "difference between"
    ]
    
    is_knowledge_request = any(keyword.lower() in user_message.lower() for keyword in knowledge_keywords)
    
    # Determine the next step
    if is_execution_request or (has_code and not is_knowledge_request):
        state["context"]["execution_explicitly_requested"] = is_execution_request
        logger.info("Next step: execute_code")
        return {"messages": messages, "next_step": "execute_code", "context": state["context"]}
    elif is_knowledge_request or len(user_message.split()) > 3:
        logger.info("Next step: retrieve_knowledge")
        return {"messages": messages, "next_step": "retrieve_knowledge", "context": state["context"]}
    else:
        logger.info("Next step: ask_clarification")
        return {"messages": messages, "next_step": "ask_clarification", "context": state["context"]}

@traceable(name="execute_code")
def execute_code(state: AgentState) -> AgentState:
    """Extract and execute Python code from user message"""
    logger.info("Executing code")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    execution_explicitly_requested = context.get("execution_explicitly_requested", False)
    
    # Extract code directly using regex pattern matching
    import re
    
    # Look for code blocks with ```python ... ``` format
    code_block_pattern = r"```(?:python)?\s*([\s\S]*?)\s*```"
    code_blocks = re.findall(code_block_pattern, user_message)
    
    # If no code blocks with markdown, try to extract all Python-like code
    if not code_blocks:
        # Assume the entire message might be code if it contains Python keywords
        python_keywords = ["import", "def", "class", "for", "while", "if", "print", "return"]
        if any(keyword in user_message for keyword in python_keywords):
            code = user_message
        else:
            # Fall back to LLM for code extraction if regex fails
            llm_messages = [
                {"role": "system", "content": "Extract the Python code from this message. Only output the code, nothing else."},
                {"role": "user", "content": user_message}
            ]
            code = call_llm(llm_messages)
    else:
        # Use the first code block found
        code = code_blocks[0]
    
    # Clean the code - ensure no markdown markers are present
    # Remove any remaining triple backticks that might be in the code
    code = re.sub(r'^```python\s*', '', code)
    code = re.sub(r'^```\s*', '', code)
    code = re.sub(r'\s*```$', '', code)
    
    logger.info(f"Extracted code: {code}")
    
    # Store the extracted code in context
    context["extracted_code"] = code
    
    # Only execute the code if explicitly requested
    if execution_explicitly_requested:
        # Execute the code in isolated container
        result = execute_code_in_container(code)
        
        # If there was an error, try to fix the code and re-execute
        if not result.get("success", False) and "error" in result and result["error"]:
            # Ask LLM to fix the code
            llm_messages = [
                {"role": "system", "content": "Fix the Python code that produced the following error. Only output the fixed code, nothing else."},
                {"role": "user", "content": f"Code:\n{code}\n\nError:\n{result['error']}"}
            ]
            fixed_code = call_llm(llm_messages)
            
            # Clean the fixed code
            fixed_code = re.sub(r'^```python\s*', '', fixed_code)
            fixed_code = re.sub(r'^```\s*', '', fixed_code)
            fixed_code = re.sub(r'\s*```$', '', fixed_code)
            
            logger.info(f"Fixed code: {fixed_code}")
            
            # Re-execute the fixed code
            fixed_result = execute_code_in_container(fixed_code)
            
            # Store both attempts in context
            context["code_execution"] = {
                "original_code": code,
                "original_result": result.get("output", ""),
                "original_success": result.get("success", False),
                "original_error": result.get("error", ""),
                "fixed_code": fixed_code,
                "fixed_result": fixed_result.get("output", ""),
                "fixed_success": fixed_result.get("success", False),
                "fixed_error": fixed_result.get("error", "")
            }
        else:
            # Store original execution in context
            context["code_execution"] = {
                "code": code,
                "result": result.get("output", ""),
                "success": result.get("success", False),
                "error": result.get("error", "")
            }
    
    logger.info("Next step: generate_response")
    return {"messages": messages, "next_step": "generate_response", "context": context}

@traceable(name="retrieve_knowledge")
def retrieve_knowledge(state: AgentState) -> AgentState:
    """Retrieve relevant Python knowledge"""
    logger.info("Retrieving knowledge")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    
    # Use invoke instead of get_relevant_documents
    docs = retriever.invoke(user_message)
    
    # Store in context
    context["retrieved_docs"] = [
        {"content": doc.page_content, "source": doc.metadata.get("source", "unknown")}
        for doc in docs
    ]
    
    logger.info("Next step: generate_response")
    return {"messages": messages, "next_step": "generate_response", "context": context}

@traceable(name="ask_clarification")
def ask_clarification(state: AgentState) -> AgentState:
    """Ask the user for clarification"""
    logger.info("Asking for clarification")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    
    llm_messages = [
        {"role": "system", "content": """You're helping someone learn Python programming.
        Generate a clarifying question to better understand their needs."""},
        {"role": "user", "content": user_message}
    ]
    
    clarification = call_llm(llm_messages)
    
    # Add to messages
    new_messages = messages.copy()
    new_messages.append({"role": "assistant", "content": clarification})
    
    logger.info("Next step: END")
    return {"messages": new_messages, "next_step": "END", "context": context}

@traceable(name="generate_response")
def generate_response(state: AgentState) -> AgentState:
    """Generate a response based on the context"""
    logger.info("Generating response")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    context_str = ""
    execution_explicitly_requested = context.get("execution_explicitly_requested", False)
    
    # Build context string
    if "retrieved_docs" in context:
        context_str += "RELEVANT KNOWLEDGE:\n"
        for doc in context["retrieved_docs"]:
            context_str += f"- {doc['content']}\n"
    
    # Handle different code execution scenarios
    if "code_execution" in context and execution_explicitly_requested:
        # Case 1: Code was executed with fix attempt
        if "original_code" in context["code_execution"]:
            code_exec = context["code_execution"]
            context_str += "\nCODE EXECUTION (ORIGINAL):\n"
            context_str += f"Code:\n{code_exec['original_code']}\n\n"
            
            if code_exec["original_success"]:
                context_str += f"Output:\n{code_exec['original_result']}\n"
            else:
                context_str += f"Error:\n{code_exec['original_error']}\n"
                
            context_str += "\nCODE EXECUTION (FIXED):\n"
            context_str += f"Code:\n{code_exec['fixed_code']}\n\n"
            
            if code_exec["fixed_success"]:
                context_str += f"Output:\n{code_exec['fixed_result']}\n"
            else:
                context_str += f"Error:\n{code_exec['fixed_error']}\n"
        
        # Case 2: Code was executed without fix attempt
        else:
            code_exec = context["code_execution"]
            context_str += "\nCODE EXECUTION:\n"
            context_str += f"Code:\n{code_exec['code']}\n\n"
            
            if code_exec["success"]:
                context_str += f"Output:\n{code_exec['result']}\n"
            else:
                context_str += f"Error:\n{code_exec['error']}\n"
    
    # Case 3: Code was extracted but not executed (just provide an explanation)
    elif "extracted_code" in context and not execution_explicitly_requested:
        context_str += "\nEXTRACTED CODE (NOT EXECUTED):\n"
        context_str += f"Code:\n{context['extracted_code']}\n\n"
    
    # Prepare system prompt based on the execution context
    system_prompt = """You're a helpful Python mentor. Based on the context and user's question,
    provide a clear, educational response with proper structure.
    
    FORMAT YOUR RESPONSE WITH THESE SECTIONS (as applicable):
    
    ## 📘 Explanation
    [Provide a clear, concise explanation of the concept or code]
    
    ## 🔍 Code Analysis
    [If code is involved, explain what it does, line by line if helpful]
    
    ## 🚀 Execution Results
    [If code was executed, explain the results]
    
    ## ⚠️ Errors & Solutions
    [If there were errors, explain them and provide solutions]
    
    ## 💡 Best Practices
    [Provide tips, improvements, or alternative approaches]
    
    ## 🔗 Related Concepts
    [Briefly mention related Python concepts the user might want to explore]
    
    Use proper markdown formatting with headings (##), bullet points (*), code formatting (`code`), 
    and other markdown elements to make your response visually structured and easy to read.
    """
    
    if execution_explicitly_requested and "code_execution" in context:
        system_prompt += """
        
        The code has been executed. Focus on explaining:
        1. What the code does
        2. The results of the execution
        3. If there were errors, explain what caused them and how they were fixed
        4. Any improvements or best practices that could be applied
        
        IMPORTANT FORMATTING INSTRUCTIONS:
        1. DO NOT include markdown code block markers (```python) in your response
        2. DO NOT repeat the code that was executed - it has already been run
        3. Format your response as a natural, conversational explanation with clear sections
        """
    elif "extracted_code" in context and not execution_explicitly_requested:
        system_prompt += """
        
        The user asked about code but didn't explicitly request execution. Provide:
        1. An explanation of what the code does
        2. Any potential issues or improvements
        3. Expected output if the code were to be executed
        
        IMPORTANT FORMATTING INSTRUCTIONS:
        1. DO NOT include markdown code block markers (```python) in your response
        2. Format your response as a natural, conversational explanation with clear sections
        """
    
    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"USER QUESTION: {user_message}\n\nCONTEXT:\n{context_str}"}
    ]
    
    response = call_llm(llm_messages)
    
    # Post-process the response to remove any markdown code blocks
    import re
    # Replace ```python ... ``` blocks with their content
    response = re.sub(r'```python\s*(.*?)\s*```', r'`\1`', response, flags=re.DOTALL)
    # Replace any remaining ``` ... ``` blocks
    response = re.sub(r'```\s*(.*?)\s*```', r'`\1`', response, flags=re.DOTALL)
    
    # Add to messages
    new_messages = messages.copy()
    new_messages.append({"role": "assistant", "content": response})
    
    logger.info("Next step: END")
    return {"messages": new_messages, "next_step": "END", "context": context}

@traceable(name="direct_response")
def direct_response(state: AgentState) -> AgentState:
    """Provide a direct response to a simple question"""
    logger.info("Providing direct response")
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    
    llm_messages = [
        {"role": "system", "content": """You're a Python mentor answering a direct question.
        Provide a clear, concise, and accurate response."""},
        {"role": "user", "content": user_message}
    ]
    
    response = call_llm(llm_messages)
    
    # Add to messages
    new_messages = messages.copy()
    new_messages.append({"role": "assistant", "content": response})
    
    logger.info("Next step: END")
    return {"messages": new_messages, "next_step": "END", "context": context}

def create_agent():
    """Create and return the agent workflow using newer LangGraph patterns"""
    logger.info("Creating agent")
    # Define a function to decide the next node based on state's next_step field
    def decide_next_step(state: AgentState) -> str:
        return state["next_step"]
    
    # Create the graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("route", route_query)
    builder.add_node("execute_code", execute_code)
    builder.add_node("retrieve_knowledge", retrieve_knowledge)
    builder.add_node("ask_clarification", ask_clarification)
    builder.add_node("generate_response", generate_response)
    builder.add_node("direct_response", direct_response)
    
    # Set the entry point
    builder.set_entry_point("route")
    
    # Add conditional edges from the router node
    builder.add_conditional_edges(
        "route",
        decide_next_step,
        {
            "execute_code": "execute_code",
            "retrieve_knowledge": "retrieve_knowledge",
            "ask_clarification": "ask_clarification", 
            "direct_response": "direct_response"
        }
    )
    
    # Add edges for the tools to the response generator
    builder.add_conditional_edges(
        "execute_code",
        decide_next_step,
        {
            "generate_response": "generate_response",
            "END": END
        }
    )
    
    builder.add_conditional_edges(
        "retrieve_knowledge",
        decide_next_step,
        {
            "generate_response": "generate_response",
            "END": END
        }
    )
    
    # Add edges to END for terminal nodes
    builder.add_edge("ask_clarification", END)
    builder.add_edge("direct_response", END)
    builder.add_edge("generate_response", END)
    
    # Compile the workflow
    logger.info("Agent created")
    return builder.compile()