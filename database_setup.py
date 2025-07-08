"""
Database setup module for creating mock dataset in PostgreSQL
"""
import os
from sqlalchemy import create_engine, text, Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    department = Column(String(50))
    salary = Column(Numeric(10, 2))
    hire_date = Column(Date)
    
    # Relationship
    sales = relationship("Sale", back_populates="employee")

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100))
    category = Column(String(50))
    price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer)
    
    # Relationship
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = 'sales'
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    sale_date = Column(Date)
    total_amount = Column(Numeric(10, 2))
    
    # Relationships
    employee = relationship("Employee", back_populates="sales")
    product = relationship("Product", back_populates="sales")

def get_db_engine():
    """Get database engine"""
    host = os.getenv('AWS_RDS_HOST')
    port = os.getenv('AWS_RDS_PORT', 5432)
    database = os.getenv('AWS_RDS_DATABASE')
    username = os.getenv('AWS_RDS_USERNAME')
    password = os.getenv('AWS_RDS_PASSWORD')
    
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string)

def create_mock_tables():
    """Create mock tables with sample data"""
    engine = get_db_engine()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if data already exists
        if session.query(Employee).count() == 0:
            # Insert sample employees
            employees = [
                Employee(first_name='John', last_name='Doe', email='john.doe@company.com', 
                        department='Sales', salary=Decimal('50000.00'), hire_date=date(2022, 1, 15)),
                Employee(first_name='Jane', last_name='Smith', email='jane.smith@company.com', 
                        department='Marketing', salary=Decimal('55000.00'), hire_date=date(2021, 8, 20)),
                Employee(first_name='Mike', last_name='Johnson', email='mike.johnson@company.com', 
                        department='Sales', salary=Decimal('52000.00'), hire_date=date(2023, 3, 10)),
                Employee(first_name='Sarah', last_name='Wilson', email='sarah.wilson@company.com', 
                        department='Engineering', salary=Decimal('75000.00'), hire_date=date(2020, 11, 5)),
                Employee(first_name='David', last_name='Brown', email='david.brown@company.com', 
                        department='Sales', salary=Decimal('48000.00'), hire_date=date(2023, 6, 12))
            ]
            session.add_all(employees)
            session.flush()  # Flush to get IDs
        
        if session.query(Product).count() == 0:
            # Insert sample products
            products = [
                Product(product_name='Laptop Pro', category='Electronics', 
                       price=Decimal('1299.99'), stock_quantity=50),
                Product(product_name='Wireless Mouse', category='Electronics', 
                       price=Decimal('29.99'), stock_quantity=200),
                Product(product_name='Office Chair', category='Furniture', 
                       price=Decimal('199.99'), stock_quantity=75),
                Product(product_name='Standing Desk', category='Furniture', 
                       price=Decimal('399.99'), stock_quantity=30),
                Product(product_name='Monitor 4K', category='Electronics', 
                       price=Decimal('299.99'), stock_quantity=80)
            ]
            session.add_all(products)
            session.flush()  # Flush to get IDs
        
        if session.query(Sale).count() == 0:
            # Insert sample sales
            sales = [
                Sale(employee_id=1, product_id=1, quantity=2, 
                    sale_date=date(2024, 1, 15), total_amount=Decimal('2599.98')),
                Sale(employee_id=1, product_id=2, quantity=5, 
                    sale_date=date(2024, 1, 16), total_amount=Decimal('149.95')),
                Sale(employee_id=3, product_id=3, quantity=1, 
                    sale_date=date(2024, 1, 17), total_amount=Decimal('199.99')),
                Sale(employee_id=5, product_id=1, quantity=1, 
                    sale_date=date(2024, 1, 18), total_amount=Decimal('1299.99')),
                Sale(employee_id=1, product_id=5, quantity=3, 
                    sale_date=date(2024, 1, 19), total_amount=Decimal('899.97')),
                Sale(employee_id=3, product_id=4, quantity=2, 
                    sale_date=date(2024, 1, 20), total_amount=Decimal('799.98')),
                Sale(employee_id=5, product_id=2, quantity=10, 
                    sale_date=date(2024, 1, 21), total_amount=Decimal('299.90'))
            ]
            session.add_all(sales)
        
        session.commit()
        print("Mock tables and data created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_mock_tables()
