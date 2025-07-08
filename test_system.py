"""
Comprehensive system test for Text2SQL Agent
"""
import os
import subprocess
from dotenv import load_dotenv
from database_setup import get_db_engine, Employee
from langchain.chat_models import init_chat_model
from sqlalchemy.orm import sessionmaker

load_dotenv()

def test_ollama():
    """Test Ollama connectivity"""
    print("🔹 Testing Ollama...")
    try:
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

        llm = init_chat_model(f"ollama:{model_name}", base_url=base_url, temperature=0)
        response = llm.invoke("What is 2+2?")
        print(f"  ✅ Ollama working - Response: {response.content}")
        return True
    except Exception as e:
        print(f"  ❌ Ollama failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("🔹 Testing Database...")
    try:
        engine = get_db_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        count = session.query(Employee).count()
        print(f"  ✅ Database working - {count} employees found")
        session.close()
        return True
    except Exception as e:
        print(f"  ❌ Database failed: {e}")
        return False

def test_full_agent():
    """Test the complete agent workflow"""
    print("🔹 Testing Complete Agent...")
    try:
        from text2sql_agent import initialize_llm, setup_database_connection, create_sql_agent, query_agent
        
        llm = initialize_llm()
        db = setup_database_connection()
        agent = create_sql_agent(llm, db)
        
        # Simple test query
        result = query_agent(agent, "How many employees are there?")
        print(f"  ✅ Agent working - Answered test question")
        return True
    except Exception as e:
        print(f"  ❌ Agent failed: {e}")
        return False

def test_gpt():
    """Test GPT connectivity"""
    print("🔹 Testing GPT...")
    try:
        gpt_model = os.getenv('GPT_MODEL', 'openai:gpt-4.1')
        
        llm = init_chat_model(gpt_model, temperature=0)
        response = llm.invoke("What is 2+2?")
        print(f"  ✅ GPT working - Response: {response.content}")
        return True
    except Exception as e:
        print(f"  ❌ GPT failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Text2SQL System Test")
    print("=" * 30)
    
    ollama_ok = test_ollama()
    gpt_ok = test_gpt()
    db_ok = test_database()
    agent_ok = test_full_agent() if (ollama_ok or gpt_ok) and db_ok else False
    
    print("\n" + "=" * 30)
    if all([db_ok, agent_ok]) and (ollama_ok or gpt_ok):
        print("🎉 All systems working!")
    else:
        print("⚠️  Some systems need attention")

if __name__ == "__main__":
    main()