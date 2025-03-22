from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
import os
from pathlib import Path
from langsmith import traceable

@traceable(name="setup_chroma_retriever")
def setup_chroma_retriever():
    """Set up and return a Chroma retriever with Python knowledge"""
    # Initialize embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Check if Chroma DB exists
    db_path = "/data/chroma"
    
    if not os.path.exists(db_path):
        # Create knowledge base with Python documentation
        python_docs = [
            {"content": "Python is a high-level, interpreted programming language known for its readability and simplicity. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.", "source": "intro.md"},
            {"content": "Python variables are dynamically typed. You don't need to declare the type of a variable when you create one. Variables are created when you assign a value to them, like x = 5 or name = 'John'.", "source": "variables.md"},
            {"content": "Functions in Python are defined using the 'def' keyword, followed by the function name and parameters in parentheses. Python functions can return values using the 'return' statement. They can also have default parameters and accept variable-length arguments.", "source": "functions.md"},
            {"content": "List comprehensions provide a concise way to create lists based on existing lists or other iterables. They consist of brackets containing an expression followed by a for clause, then zero or more for or if clauses. Example: [x**2 for x in range(10) if x % 2 == 0]", "source": "list_comprehensions.md"},
            {"content": "Python dictionaries are collections of key-value pairs. They are mutable and unordered. Keys must be unique and immutable (strings, numbers, tuples). Values can be of any type and can be duplicated. Example: my_dict = {'name': 'John', 'age': 30}", "source": "dictionaries.md"},
            {"content": "Python classes are created using the 'class' keyword. Objects are instances of classes. Methods are functions defined within classes. The first parameter of a method is always 'self', which refers to the instance of the class. Example: class Person: def __init__(self, name): self.name = name", "source": "classes.md"},
            {"content": "Exception handling in Python is done using try, except, else, and finally blocks. Try blocks contain code that might raise exceptions. Except blocks handle specific exceptions. Else blocks run if no exceptions occur. Finally blocks always execute, regardless of whether an exception occurred.", "source": "exceptions.md"},
            {"content": "Python decorators are functions that modify the behavior of other functions. They are denoted by the '@' symbol followed by the decorator name above the function definition. Decorators are a powerful way to add functionality to existing functions without modifying their code.", "source": "decorators.md"},
            {"content": "The Python standard library includes modules for file I/O operations. The 'open()' function is used to open files, with modes like 'r' for reading, 'w' for writing, and 'a' for appending. It's best to use the 'with' statement to ensure files are properly closed after use.", "source": "file_io.md"},
            {"content": "Python generators are functions that use the 'yield' statement to return values one at a time, pausing execution between calls. They are memory-efficient for working with large datasets or infinite sequences. Generator expressions are similar to list comprehensions but use parentheses instead of brackets.", "source": "generators.md"},
        ]
        
        # Convert to documents
        documents = [
            Document(page_content=doc["content"], metadata={"source": doc["source"]})
            for doc in python_docs
        ]
        
        # Create vector store
        db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=db_path
        )
        db.persist()
    else:
        # Load existing vector store
        db = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )
    
    # Create and return retriever
    return db.as_retriever(search_kwargs={"k": 3})