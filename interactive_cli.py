"""
Interactive CLI for Text-to-SQL Agent
"""
import os
import sys
from text2sql_agent import initialize_llm, setup_database_connection, create_sql_agent, query_agent

def interactive_mode():
    """Run the agent in interactive mode"""
    print("Text-to-SQL Agent Interactive Mode")
    print("=" * 40)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for sample questions")
    print()
    
    try:
        # Initialize components
        llm = initialize_llm()
        db = setup_database_connection()
        agent = create_sql_agent(llm, db)
        
        while True:
            question = input("\nEnter your question: ").strip()
            
            if question.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if question.lower() == 'help':
                show_help()
                continue
            
            if not question:
                print("Please enter a question.")
                continue
            
            query_agent(agent, question)
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")

def show_help():
    """Show sample questions"""
    print("\nSample questions you can ask:")
    print("- How many employees are in each department?")
    print("- What are the top 3 best-selling products?")
    print("- Which employee made the most sales?")
    print("- Show me all products with their prices")
    print("- What is the average salary by department?")
    print("- List all sales from January 2024")

if __name__ == "__main__":
    interactive_mode()
