import os
import json
import requests
import time
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from langsmith import traceable
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from tools.code_executor import execute_code_in_container
from tools.retriever import setup_chroma_retriever

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
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=temperature,
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )

# Define a direct LLM call function
def call_llm(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """Call LLM via local LiteLLM server with fallback to direct API"""
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
                print("Using LiteLLM service")
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"LiteLLM error (attempt {attempt+1}/{max_retries}): {response.status_code}")
                print(f"Response content: {response.text}")
                if attempt == max_retries - 1:
                    # Last attempt, fall back to direct API
                    raise Exception(f"LiteLLM error after {max_retries} attempts: {response.text}")
                # Wait before retrying
                time.sleep(2)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"All LiteLLM attempts failed, using direct API: {e}")
                # Fall back to direct API call on the last attempt
                llm = get_llm(temperature)
                response = llm.invoke([{"role": m["role"], "content": m["content"]} for m in messages])
                return response.content
            print(f"LiteLLM attempt {attempt+1} failed: {e}")
            time.sleep(2)  # Wait before retry
    
    # If we get here, all retries failed
    llm = get_llm(temperature)
    response = llm.invoke([{"role": m["role"], "content": m["content"]} for m in messages])
    return response.content

# Router function
@traceable(name="route_query")
def route_query(state: AgentState) -> AgentState:
    """Determine the next step based on the user query"""
    messages = state["messages"]
    user_message = messages[-1]["content"]
    
    llm_messages = [
        {"role": "system", "content": """You're a Python mentor bot that categorizes user questions.
        Based on the query, decide which action to take by choosing EXACTLY ONE of these options:
        - code_execution: If they want to run Python code
        - knowledge_retrieval: If they're asking about Python concepts
        - direct_response: For simple questions you can answer directly
        - ask_clarification: If you need clarification
        
        Reply with ONLY ONE of these exact category names and nothing else."""},
        {"role": "user", "content": user_message}
    ]
    
    try:
        result = call_llm(llm_messages).strip().lower()
        print(f"Routing decision: {result}")
        
        if "code" in result:
            return {"messages": messages, "next_step": "code_execution", "context": state["context"]}
        elif "knowledge" in result or "retriev" in result:
            return {"messages": messages, "next_step": "knowledge_retrieval", "context": state["context"]}
        elif "ask" in result or "clarif" in result:
            return {"messages": messages, "next_step": "ask_clarification", "context": state["context"]}
        else:
            return {"messages": messages, "next_step": "direct_response", "context": state["context"]}
    except Exception as e:
        print(f"Error in routing: {e}")
        return {"messages": messages, "next_step": "direct_response", "context": state["context"]}

@traceable(name="execute_code")
def execute_code(state: AgentState) -> AgentState:
    """Extract and execute Python code from user message"""
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    
    # Extract code
    llm_messages = [
        {"role": "system", "content": "Extract the Python code from this message. Only output the code, nothing else."},
        {"role": "user", "content": user_message}
    ]
    
    code = call_llm(llm_messages)
    
    # Execute the code in isolated container
    result = execute_code_in_container(code)
    
    # Store in context
    context["code_execution"] = {
        "code": code,
        "result": result.get("output", ""),
        "success": result.get("success", False),
        "error": result.get("error", "")
    }
    
    return {"messages": messages, "next_step": "generate_response", "context": context}

@traceable(name="retrieve_knowledge")
def retrieve_knowledge(state: AgentState) -> AgentState:
    """Retrieve relevant Python knowledge"""
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
    
    return {"messages": messages, "next_step": "generate_response", "context": context}

@traceable(name="ask_clarification")
def ask_clarification(state: AgentState) -> AgentState:
    """Ask the user for clarification"""
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
    
    return {"messages": new_messages, "next_step": "END", "context": context}

@traceable(name="generate_response")
def generate_response(state: AgentState) -> AgentState:
    """Generate a response based on the context"""
    messages = state["messages"]
    user_message = messages[-1]["content"]
    context = state["context"]
    context_str = ""
    
    # Build context string
    if "retrieved_docs" in context:
        context_str += "RELEVANT KNOWLEDGE:\n"
        for doc in context["retrieved_docs"]:
            context_str += f"- {doc['content']}\n"
    
    if "code_execution" in context:
        code_exec = context["code_execution"]
        context_str += "\nCODE EXECUTION:\n"
        context_str += f"```python\n{code_exec['code']}\n```\n\n"
        
        if code_exec["success"]:
            context_str += f"Output:\n{code_exec['result']}\n"
        else:
            context_str += f"Error:\n{code_exec['error']}\n"
    
    llm_messages = [
        {"role": "system", "content": """You're a helpful Python mentor. Based on the context and user's question,
        provide a clear, educational response. If there's code execution, explain the results.
        If there were errors, suggest fixes. If knowledge was retrieved, use it in your answer."""},
        {"role": "user", "content": f"USER QUESTION: {user_message}\n\nCONTEXT:\n{context_str}"}
    ]
    
    response = call_llm(llm_messages)
    
    # Add to messages
    new_messages = messages.copy()
    new_messages.append({"role": "assistant", "content": response})
    
    return {"messages": new_messages, "next_step": "END", "context": context}

@traceable(name="direct_response")
def direct_response(state: AgentState) -> AgentState:
    """Provide a direct response to a simple question"""
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
    
    return {"messages": new_messages, "next_step": "END", "context": context}

def create_agent():
    """Create and return the agent workflow using newer LangGraph patterns"""
    # Define a function to decide the next node based on state's next_step field
    def decide_next_step(state: AgentState) -> str:
        return state["next_step"]
    
    # Create the graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("route", route_query)
    builder.add_node("code_execution", execute_code)
    builder.add_node("knowledge_retrieval", retrieve_knowledge)
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
            "code_execution": "code_execution",
            "knowledge_retrieval": "knowledge_retrieval",
            "ask_clarification": "ask_clarification", 
            "direct_response": "direct_response"
        }
    )
    
    # Add edges for the tools to the response generator
    builder.add_conditional_edges(
        "code_execution",
        decide_next_step,
        {
            "generate_response": "generate_response",
            "END": END
        }
    )
    
    builder.add_conditional_edges(
        "knowledge_retrieval",
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
    return builder.compile()