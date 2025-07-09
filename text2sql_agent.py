import os
from typing import List, Dict, Any, Literal
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langsmith import traceable

load_dotenv()

def initialize_llm():
    """Initialize the LLM using open-source model via Ollama or GPT"""
    model_name = os.getenv('GPT_MODEL', 'openai:gpt-4.1')
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    return init_chat_model(
        model=model_name,
        # base_url=base_url,
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

@traceable(name="create_sql_agent", run_type="tool")
def create_sql_agent(llm, db: SQLDatabase):
    """Create the custom SQL agent using Graph API"""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Extract specific tools
    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    get_schema_node = ToolNode([get_schema_tool], name="get_schema")
    
    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    run_query_node = ToolNode([run_query_tool], name="run_query")
    
    # Node functions
    def list_tables(state: MessagesState):
        """Force a call to list all tables in the database"""
        tool_call = {
            "name": "sql_db_list_tables",
            "args": {},
            "id": "list_tables_call",
            "type": "tool_call",
        }
        tool_call_message = AIMessage(content="", tool_calls=[tool_call])
        
        list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
        tool_message = list_tables_tool.invoke(tool_call)
        response = AIMessage(f"Available tables: {tool_message.content}")
        
        return {"messages": [tool_call_message, tool_message, response]}
    
    def call_get_schema(state: MessagesState):
        """Force the model to get schema for relevant tables"""
        llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def generate_query(state: MessagesState):
        """Generate SQL query based on the question and schema"""
        generate_query_system_prompt = f"""
        You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct {db.dialect} query to run,
        then look at the results of the query and return the answer. Unless the user
        specifies a specific number of examples they wish to obtain, always limit your
        query to at most 5 results.

        You can order the results by a relevant column to return the most interesting
        examples in the database. Never query for all the columns from a specific table,
        only ask for the relevant columns given the question.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
        """
        
        system_message = {
            "role": "system", 
            "content": generate_query_system_prompt,
        }
        
        # We do not force a tool call here to allow natural responses
        llm_with_tools = llm.bind_tools([run_query_tool])
        response = llm_with_tools.invoke([system_message] + state["messages"])
        
        return {"messages": [response]}
    
    def check_query(state: MessagesState):
        """Double-check the SQL query for common mistakes"""
        check_query_system_prompt = f"""
        You are a SQL expert with a strong attention to detail.
        Double check the {db.dialect} query for common mistakes, including:
        - Using NOT IN with NULL values
        - Using UNION when UNION ALL should have been used
        - Using BETWEEN for exclusive ranges
        - Data type mismatch in predicates
        - Properly quoting identifiers
        - Using the correct number of arguments for functions
        - Casting to the correct data type
        - Using the proper columns for joins

        If there are any of the above mistakes, rewrite the query. If there are no mistakes,
        just reproduce the original query.

        You will call the appropriate tool to execute the query after running this check.
        """
        
        system_message = {
            "role": "system",
            "content": check_query_system_prompt,
        }
        
        # Generate an artificial user message to check
        tool_call = state["messages"][-1].tool_calls[0]
        user_message = {"role": "user", "content": tool_call["args"]["query"]}
        llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
        response = llm_with_tools.invoke([system_message, user_message])
        response.id = state["messages"][-1].id
        
        return {"messages": [response]}
    
    def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
        """Determine whether to continue with query checking or end"""
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return END
        else:
            return "check_query"
    
    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("list_tables", list_tables)
    builder.add_node("call_get_schema", call_get_schema)
    builder.add_node("get_schema", get_schema_node)
    builder.add_node("generate_query", generate_query)
    builder.add_node("check_query", check_query)
    builder.add_node("run_query", run_query_node)
    
    # Define the workflow
    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges(
        "generate_query",
        should_continue,
    )
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")
    
    return builder.compile()

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

@traceable(name="text2sql_agent_main")
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
        
        png_bytes = agent.get_graph().draw_mermaid_png()

        with open("graph.png", "wb") as f:
            f.write(png_bytes)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
