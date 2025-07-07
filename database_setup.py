"""
Database setup module for creating mock dataset in PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('AWS_RDS_HOST'),
        port=os.getenv('AWS_RDS_PORT', 5432),
        database=os.getenv('AWS_RDS_DATABASE'),
        user=os.getenv('AWS_RDS_USERNAME'),
        password=os.getenv('AWS_RDS_PASSWORD')
    )

def create_mock_tables():
    """Create mock tables with sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                department VARCHAR(50),
                salary DECIMAL(10,2),
                hire_date DATE
            );
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100),
                category VARCHAR(50),
                price DECIMAL(10,2),
                stock_quantity INTEGER
            );
        """)
        
        # Create sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees(employee_id),
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER,
                sale_date DATE,
                total_amount DECIMAL(10,2)
            );
        """)
        
        # Insert sample data
        employees_data = [
            ('John', 'Doe', 'john.doe@company.com', 'Sales', 50000.00, '2022-01-15'),
            ('Jane', 'Smith', 'jane.smith@company.com', 'Marketing', 55000.00, '2021-08-20'),
            ('Mike', 'Johnson', 'mike.johnson@company.com', 'Sales', 52000.00, '2023-03-10'),
            ('Sarah', 'Wilson', 'sarah.wilson@company.com', 'Engineering', 75000.00, '2020-11-05'),
            ('David', 'Brown', 'david.brown@company.com', 'Sales', 48000.00, '2023-06-12')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, employees_data)
        
        products_data = [
            ('Laptop Pro', 'Electronics', 1299.99, 50),
            ('Wireless Mouse', 'Electronics', 29.99, 200),
            ('Office Chair', 'Furniture', 199.99, 75),
            ('Standing Desk', 'Furniture', 399.99, 30),
            ('Monitor 4K', 'Electronics', 299.99, 80)
        ]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO products (product_name, category, price, stock_quantity)
                VALUES (%s, %s, %s, %s)
            """, products_data)
        
        sales_data = [
            (1, 1, 2, '2024-01-15', 2599.98),
            (1, 2, 5, '2024-01-16', 149.95),
            (3, 3, 1, '2024-01-17', 199.99),
            (5, 1, 1, '2024-01-18', 1299.99),
            (1, 5, 3, '2024-01-19', 899.97),
            (3, 4, 2, '2024-01-20', 799.98),
            (5, 2, 10, '2024-01-21', 299.90)
        ]
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO sales (employee_id, product_id, quantity, sale_date, total_amount)
                VALUES (%s, %s, %s, %s, %s)
            """, sales_data)
        
        conn.commit()
        print("Mock tables and data created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_mock_tables()
