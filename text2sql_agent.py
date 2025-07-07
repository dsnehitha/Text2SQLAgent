"""
Text-to-SQL Agent using LangChain and LangGraph with Open Source Models
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

load_dotenv()

def initialize_llm():
    """Initialize the LLM using open-source model via Ollama"""
    model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    return init_chat_model(
        model=f"ollama:{model_name}",
        base_url=base_url,
        temperature=0
    )

def setup_database_connection() -> SQLDatabase:
    """Setup database connection to PostgreSQL"""
    host = os.getenv('AWS_RDS_HOST')
    port = os.getenv('AWS_RDS_PORT', 5432)
    database = os.getenv('AWS_RDS_DATABASE')
    username = os.getenv('AWS_RDS_USERNAME')
    password = os.getenv('AWS_RDS_PASSWORD')
    
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    db = SQLDatabase.from_uri(connection_string)
    
    print(f"Database dialect: {db.dialect}")
    print(f"Available tables: {db.get_usable_table_names()}")
    
    return db

def create_sql_agent(llm, db: SQLDatabase):
    """Create the SQL agent with tools"""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
        dialect=db.dialect,
        top_k=5,
    )
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
    )
    
    return agent

def query_agent(agent, question: str) -> List[Dict[str, Any]]:
    """Query the agent with a question"""
    print(f"\nQuerying: {question}")
    print("-" * 50)
    
    messages = []
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
    ):
        messages.append(step["messages"][-1])
        step["messages"][-1].pretty_print()
    
    return messages

def main():
    """Main function to run the text-to-SQL agent"""
    try:
        # Initialize components
        llm = initialize_llm()
        db = setup_database_connection()
        agent = create_sql_agent(llm, db)
        
        # Sample queries
        sample_questions = [
            # "How many employees are in each department?",
            # "What are the top 3 best-selling products by revenue?",
            # "Which employee made the most sales in 2024?",
            # "Show me all products in the Electronics category with their prices",
            "What is the average salary by department?"
        ]
        
        print("\nRunning sample queries...")
        print("=" * 60)
        
        for question in sample_questions:
            query_agent(agent, question)
            print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
