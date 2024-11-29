import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
# Load the MySQL root password from environment variables
# mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {
    'host': 'mysql',
    'database_name': 'hr',
    'user': 'root',
    'password': 'a301rrhh' 
    }

# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}:3306', echo=True)
engine = create_engine('mysql+pymysql://root:a301rrhh@mysql:3306')

with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS hr"))
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}:3306/{config["database_name"]}', echo=True)
engine = create_engine('mysql+pymysql://root:a301rrhh@mysql:3306/hr')

Base = declarative_base()

# Company model
class Company(Base):
    __tablename__ = 'Company'
    id = Column(Integer, primary_key=True)
    rut = Column(String(20))  # Equivalent to 'rut'
    name = Column(String(100))
    address = Column(String(255))
    phone = Column(String(20))
    industry = Column(String(100))  # Equivalent to 'giro'

# Employee model
class Employee(Base):
    __tablename__ = 'Employee'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String(20))  # Equivalent to 'rut'
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date)
    start_date = Column(Date)
    email = Column(String(320))
    phone = Column(String(20))
    salary = Column(DECIMAL(10, 2))
    nationality = Column(String(50))
    active_employee = Column(Boolean, default=True)
    afp_id = Column(Integer, ForeignKey('AFP.id'))
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    afp = relationship('AFP', back_populates='employees')  # Relationship to AFP
    health_plan = relationship('HealthPlan', back_populates='employees')  # Relationship to HealthPlan
    contracts = relationship('Contract', back_populates='employees')
    vacations = relationship('Vacation', back_populates='employees')
    evaluations = relationship('Evaluation', back_populates='employees')
    trainings = relationship('Training', back_populates='employees')
    remunerations = relationship('Remuneration', back_populates='employees')
    job_positions = relationship('JobPosition', secondary='EmployeePosition', back_populates='employees')  # Many-to-Many with JobPosition

# Department model
class Department(Base):
    __tablename__ = 'Department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    job_positions = relationship('JobPosition', back_populates='departments')  # Relationship to JobPosition

# Position model
class JobPosition(Base):
    __tablename__ = 'JobPosition'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    department_id = Column(Integer, ForeignKey('Department.id'))  # Foreign key to Department
    departments = relationship('Department', back_populates='job_positions')  # Relationship to Department
    employees = relationship('Employee', secondary='EmployeePosition', back_populates='job_positions')  # Relationship to Employee

# EmployeePosition association table (Many-to-Many relationship between Employee and JobPosition)
class EmployeePosition(Base):
    __tablename__ = 'EmployeePosition'
    employee_id = Column(Integer, ForeignKey('Employee.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('JobPosition.id'), primary_key=True)

# Pension Fund model (AFP)
class AFP(Base):
    __tablename__ = 'AFP'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    commission_percentage = Column(DECIMAL(5, 2))
    employees = relationship('Employee', back_populates='afp')
    remunerations = relationship('Remuneration', back_populates='afps')

# Vacation model
class Vacation(Base):
    __tablename__ = 'Vacation'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    days_taken = Column(Integer)
    accumulated_days = Column(Integer, default = 15)
    long_service_employee = Column(Boolean) 
    employees = relationship('Employee', back_populates='vacations')

# Evaluation model
class Evaluation(Base):
    __tablename__ = 'Evaluation'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    evaluation_date = Column(Date)
    evaluator = Column(String(100))
    evaluation_factor = Column(DECIMAL(5, 2))
    rating = Column(String(50))  # Good, average, bad/deficient
    comments = Column(Text)
    employees = relationship('Employee', back_populates='evaluations')

# Training model
class Training(Base):
    __tablename__ = 'Training'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    training_date = Column(Date)
    course = Column(String(100))
    score = Column(DECIMAL(5, 2))
    institution = Column(String(100))
    comments = Column(Text)
    employees = relationship('Employee', back_populates='trainings')

# Remuneration model
class Remuneration(Base):
    __tablename__ = 'Remuneration'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    afp_id = Column(Integer, ForeignKey('AFP.id'))
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    gross_amount = Column(DECIMAL(10, 2))
    tax = Column(DECIMAL(5, 2))
    deductions = Column(DECIMAL(10, 2))
    bonus = Column(DECIMAL(10, 2))
    welfare_contribution = Column(DECIMAL(10, 2))
    net_amount = Column(DECIMAL(10, 2))
    employees = relationship('Employee', back_populates='remunerations')
    afps = relationship('AFP', back_populates='remunerations')
    health_plans = relationship('HealthPlan', back_populates='remunerations')

# HealthPlan model
class HealthPlan(Base):
    __tablename__ = 'HealthPlan'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    type = Column(String(50))
    employees = relationship('Employee', back_populates='health_plan')
    fonasa = relationship('Fonasa', back_populates='health_plans')
    isapre = relationship('Isapre', back_populates='health_plans')
    remunerations = relationship('Remuneration', back_populates='health_plans')

# Public Health model (Fonasa)
class Fonasa(Base):
    __tablename__ = 'Fonasa'
    id = Column(Integer, primary_key=True)
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    discount = Column(DECIMAL(10, 2))  # Equivalent to 'descuento'
    health_plans = relationship('HealthPlan', back_populates='fonasa')

# PrivateHealth model (Isapre)
class Isapre(Base):
    __tablename__ = 'Isapre'
    id = Column(Integer, primary_key=True)
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    discount = Column(DECIMAL(10, 2)) 
    health_plans = relationship('HealthPlan', back_populates='isapre')

# Contract model
class Contract(Base):
    __tablename__ = 'Contract'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    contract_type = Column(String(50))  # Fixed, temporary, replacement, permanent (contrata, suplencia, reemplazo, planta)
    start_date = Column(Date)
    end_date = Column(Date)
    classification = Column(String(50))  # Auxiliary, administrative, technical, professional, executive (escalafon)
    registration_date = Column(Date)
    employees = relationship('Employee', back_populates='contracts')  # Relationship to Employee

Base.metadata.create_all(engine)
