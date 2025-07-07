# Text2SQLAgent

A LangChain-based agent that converts natural language questions into SQL queries and executes them against a PostgreSQL database on AWS using open-source LLMs via Ollama.

## Features

- Text-to-SQL conversion using LangChain and LangGraph
- **Open-source LLM support via Ollama** (no API keys required!)
- PostgreSQL database integration on AWS RDS
- Pre-built mock dataset (employees, products, sales)
- Interactive CLI interface
- Automated query validation and error correction
- **Comprehensive system testing**

## Quick Start

1. **Install Ollama**
   ```bash
   # On macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or visit https://ollama.ai/download
   ```

2. **Setup Environment & Run Tests**
   ```bash
   ./setup.sh
   ```

3. **Start Ollama Server** (if not already running)
   ```bash
   ollama serve
   ```

4. **Configure Credentials**
   Edit `.env` file with your credentials:
   ```
   # Ollama settings (adjust model as needed)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b
   
   # AWS RDS settings
   AWS_RDS_HOST=your_aws_rds_host
   AWS_RDS_DATABASE=text2sql_db
   AWS_RDS_USERNAME=your_username
   AWS_RDS_PASSWORD=your_password
   ```

5. **Create Mock Dataset**
   ```bash
   python database_setup.py
   ```

6. **Verify System Health**
   ```bash
   python test_system.py
   ```

7. **Run the Agent**
   ```bash
   # Demo mode with sample queries
   python text2sql_agent.py
   
   # Interactive mode
   python interactive_cli.py
   ```

## Troubleshooting

If you encounter issues, run the system test to diagnose:
```bash
python test_system.py
```

## Supported Models

The agent uses Ollama for running open-source models locally. 

To change models, update the `OLLAMA_MODEL` in your `.env` file and run:
```bash
ollama pull <model-name>
```

## Database Schema

The mock dataset includes three tables:

- **employees**: employee_id, first_name, last_name, email, department, salary, hire_date
- **products**: product_id, product_name, category, price, stock_quantity  
- **sales**: sale_id, employee_id, product_id, quantity, sale_date, total_amount


## Architecture

```
User Question
     ↓
┌─────────────────┐
│   Text2SQL      │
│     Agent       │ ← Ollama LLM (llama3.2:3b)
│  (LangGraph)    │
└─────────────────┘
     ↓
┌─────────────────┐
│  SQL Toolkit    │
│ • List Tables   │
│ • Get Schemas   │
│ • Execute Query │
│ • Validate SQL  │
└─────────────────┘
     ↓
┌─────────────────┐
│   PostgreSQL    │
│   (AWS RDS)     │
│                 │
│ employees       │
│ products        │
│ sales           │
└─────────────────┘
     ↓
Natural Language Answer
```

**Flow**: Question → Agent Analysis → SQL Generation → Database Query → Formatted Response

**Key Components**: LangGraph ReAct Agent + Ollama LLM + PostgreSQL + Error Correction Loop
