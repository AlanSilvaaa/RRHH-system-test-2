import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# Load the MySQL root password from environment variables
# mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set

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
    id = Column(Integer, primary_key=True)
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
    accumulated_days = Column(Integer)
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
# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into Company table
company_data = [
    # Fictional Media Companies
    {'id': 1, 'rut': '80.345.678-9', 'name': 'Capsule Corp', 'address': '1 Capsule Blvd, West City', 'phone': '555-0300', 'industry': 'Technology'},
    {'id': 2, 'rut': '80.456.789-0', 'name': 'Los Pollos Hermanos', 'address': '123 Chicken Lane, Albuquerque', 'phone': '555-0400', 'industry': 'Food & Restaurant'},
    {'id': 3, 'rut': '81.567.890-1', 'name': 'Wayne Enterprises', 'address': '1007 Gotham City St', 'phone': '555-0500', 'industry': 'Technology'},
    {'id': 4, 'rut': '82.678.901-2', 'name': 'Stark Industries', 'address': '10880 Malibu Point, California', 'phone': '555-0600', 'industry': 'Technology'},
    {'id': 5, 'rut': '83.789.012-3', 'name': 'Umbrella Corporation', 'address': '1 Raccoon City', 'phone': '555-0700', 'industry': 'Pharmaceuticals'},
    {'id': 6, 'rut': '84.890.123-4', 'name': 'NERV', 'address': '2 Shiroyama, Tokyo-3', 'phone': '555-0800', 'industry': 'Defense & Research'},
    
    # Famous Gaming Companies
    {'id': 7, 'rut': '85.901.234-5', 'name': 'Bethesda Game Studios', 'address': '123 Elder Scrolls Blvd', 'phone': '555-0900', 'industry': 'Gaming'},
    {'id': 8, 'rut': '86.012.345-6', 'name': 'Xbox Game Studios', 'address': '1 Xbox Plaza, Redmond', 'phone': '555-1000', 'industry': 'Gaming'},
    {'id': 9, 'rut': '87.123.456-7', 'name': 'Netease', 'address': '999 Game Ave, Hangzhou', 'phone': '555-1100', 'industry': 'Gaming'},
    {'id': 10, 'rut': '88.234.567-8', 'name': 'Square Enix', 'address': '1-6-1, Shinjuku, Tokyo', 'phone': '555-1200', 'industry': 'Gaming'},
    {'id': 11, 'rut': '89.345.678-9', 'name': 'Ubisoft', 'address': '28 Rue Armand Carrel, Paris', 'phone': '555-1300', 'industry': 'Gaming'},
    {'id': 12, 'rut': '90.456.789-0', 'name': 'Valve Corporation', 'address': '104 2nd Ave, Bellevue', 'phone': '555-1400', 'industry': 'Gaming'},
    {'id': 13, 'rut': '91.567.890-1', 'name': 'Capcom', 'address': '3-1-1, Shibuya, Tokyo', 'phone': '555-1500', 'industry': 'Gaming'},
    {'id': 14, 'rut': '92.678.901-2', 'name': 'Nintendo', 'address': '11-1, Kamitoba, Kyoto', 'phone': '555-1600', 'industry': 'Gaming'},
    {'id': 15, 'rut': '93.789.012-3', 'name': 'Re-Logic', 'address': '7000 W. Sligh Ave, Tampa', 'phone': '555-1700', 'industry': 'Gaming'},
    {'id': 16, 'rut': '94.890.123-4', 'name': 'Riot Games', 'address': '123 Riot Ave, Los Angeles', 'phone': '555-1800', 'industry': 'Gaming'},
    {'id': 17, 'rut': '95.901.234-5', 'name': 'Blizzard Entertainment', 'address': '1 Blizzard Way, Irvine', 'phone': '555-1900', 'industry': 'Gaming'}
]

for data in company_data:
    company = Company(**data)
    session.add(company)
session.commit()

# Insert data into AFP table
afp_data = [
    {'id': 1, 'name': 'AFP Capital', 'commission_percentage': 1.44},
    {'id': 2, 'name': 'AFP Cuprum', 'commission_percentage': 1.44},
    {'id': 3, 'name': 'AFP Habitat', 'commission_percentage': 1.27},
    {'id': 4, 'name': 'AFP Modelo', 'commission_percentage': 0.58},
    {'id': 5, 'name': 'AFP Planvital', 'commission_percentage': 1.16},
    {'id': 6, 'name': 'AFP Provida', 'commission_percentage': 1.45},
    {'id': 7, 'name': 'AFP Uno', 'commission_percentage': 0.49}
]

for data in afp_data:
    afp = AFP(**data)
    session.add(afp)
session.commit()

# Insert data into HealthPlan, Fonasa, and Isapre tables
health_plan_data = [
    {'id': 1, 'name': 'Plan A', 'type': 'Fonasa'},
    {'id': 2, 'name': 'Plan B', 'type': 'Fonasa'},
    {'id': 3, 'name': 'Plan C', 'type': 'Fonasa'},
    {'id': 4, 'name': 'Plan D', 'type': 'Fonasa'},
    {'id': 5, 'name': 'Banmédica S.A.', 'type': 'Isapre'},
    {'id': 6, 'name': 'Isalud Ltda.', 'type': 'Isapre'},
    {'id': 7, 'name': 'Colmena Golden Cross S.A.', 'type': 'Isapre'},
    {'id': 8, 'name': 'Consalud S.A.', 'type': 'Isapre'},
    {'id': 9, 'name': 'Cruz Blanca S.A.', 'type': 'Isapre'},
    {'id': 10, 'name': 'Cruz del Norte Ltda.', 'type': 'Isapre'},
    {'id': 11, 'name': 'Nueva Masvida S.A.', 'type': 'Isapre'},
    {'id': 12, 'name': 'Fundación Ltda.', 'type': 'Isapre'},
    {'id': 13, 'name': 'Vida Tres S.A.', 'type': 'Isapre'},
    {'id': 14, 'name': 'Esencial S.A.', 'type': 'Isapre'}
]

for data in health_plan_data:
    health_plan = HealthPlan(**data)
    session.add(health_plan)
session.commit()

# Insert data into Fonasa table
fonasa_data = [
    {'id': 1, 'health_plan_id': 1, 'discount': 4.00},
    {'id': 2, 'health_plan_id': 2, 'discount': 6.00},
    {'id': 3, 'health_plan_id': 3, 'discount': 7.00},
    {'id': 4, 'health_plan_id': 4, 'discount': 7.00},
]

for data in fonasa_data:
    fonasa = Fonasa(**data)
    session.add(fonasa)
session.commit()

# Insert data into Isapre table
isapre_data = [
    {'id': 1, 'health_plan_id': 5, 'discount': 10.00},
    {'id': 2, 'health_plan_id': 6, 'discount': 12.00},
    {'id': 3, 'health_plan_id': 7, 'discount': 8.50},
    {'id': 4, 'health_plan_id': 8, 'discount': 15.00},
    {'id': 5, 'health_plan_id': 9, 'discount': 9.00},
    {'id': 6, 'health_plan_id': 10, 'discount': 11.00},
    {'id': 7, 'health_plan_id': 11, 'discount': 13.50},
    {'id': 8, 'health_plan_id': 12, 'discount': 10.00},
    {'id': 9, 'health_plan_id': 13, 'discount': 14.00},
    {'id': 10, 'health_plan_id': 14, 'discount': 16.00}
]

for data in isapre_data:
    isapre = Isapre(**data)
    session.add(isapre)
session.commit()

# Insert data into Employee table
employee_data = [
    {'id': 1, 'rut': '20.890.678-9', 'first_name': 'John', 'last_name': 'Doe', 'birth_date': date(2000, 9, 18), 'start_date': date(2023, 1, 15), 'phone': '555-2345', 'email': 'john.doe@psyonix.com', 'salary': 1200.00, 'nationality': 'Chilean', 'active_employee': True, 'afp_id': 7, 'health_plan_id': 1},
    {'id': 2, 'rut': '12.345.678-1', 'first_name': 'Mary', 'last_name': 'Johnson', 'birth_date': date(1985, 9, 22), 'start_date': date(2019, 3, 10), 'phone': '555-6789', 'email': 'mary.johnson@psyonix.com', 'salary': 2500.00, 'nationality': 'American', 'active_employee': True, 'afp_id': 2, 'health_plan_id': 2},
    {'id': 3, 'rut': '13.345.678-2', 'first_name': 'Carlos', 'last_name': 'Williams', 'birth_date': date(1990, 7, 18), 'start_date': date(2021, 6, 5), 'phone': '555-9102', 'email': 'carlos.williams@psyonix.com', 'salary': 1800.00, 'nationality': 'Mexican', 'active_employee': False, 'afp_id': 3, 'health_plan_id': 3},
    {'id': 4, 'rut': '14.345.678-3', 'first_name': 'Anna', 'last_name': 'Brown', 'birth_date': date(1992, 11, 2), 'start_date': date(2018, 9, 25), 'phone': '555-1124', 'email': 'anna.brown@psyonix.com', 'salary': 2300.00, 'nationality': 'British', 'active_employee': False, 'afp_id': 4, 'health_plan_id': 1},
    {'id': 5, 'rut': '18.145.678-4', 'first_name': 'Louis', 'last_name': 'Davis', 'birth_date': date(1995, 2, 15), 'start_date': date(2022, 2, 1), 'phone': '555-1416', 'email': 'louis.davis@psyonix.com', 'salary': 2100.00, 'nationality': 'Canadian', 'active_employee': True, 'afp_id': 5, 'health_plan_id': 2},
    {'id': 6, 'rut': '16.245.678-5', 'first_name': 'Laura', 'last_name': 'Miller', 'birth_date': date(1997, 6, 25), 'start_date': date(2020, 8, 14), 'phone': '555-1718', 'email': 'laura.miller@psyonix.com', 'salary': 2400.00, 'nationality': 'German', 'active_employee': True, 'afp_id': 6, 'health_plan_id': 3},
    {'id': 7, 'rut': '16.645.678-6', 'first_name': 'Robert', 'last_name': 'Wilson', 'birth_date': date(1987, 4, 8), 'start_date': date(2017, 10, 12), 'phone': '555-1920', 'email': 'robert.wilson@psyonix.com', 'salary': 2200.00, 'nationality': 'Australian', 'active_employee': False, 'afp_id': 7, 'health_plan_id': 4},
    {'id': 8, 'rut': '12.945.678-7', 'first_name': 'Fernanda', 'last_name': 'Taylor', 'birth_date': date(1988, 1, 3), 'start_date': date(2021, 4, 8), 'phone': '555-2021', 'email': 'fernanda.taylor@psyonix.com', 'salary': 2700.00, 'nationality': 'Brazilian', 'active_employee': True, 'afp_id': 1, 'health_plan_id': 5},
    {'id': 9, 'rut': '14.745.678-8', 'first_name': 'George', 'last_name': 'Anderson', 'birth_date': date(1986, 12, 20), 'start_date': date(2020, 3, 14), 'phone': '555-2223', 'email': 'george.anderson@psyonix.com', 'salary': 2600.00, 'nationality': 'American', 'active_employee': False, 'afp_id': 2, 'health_plan_id': 6},
    {'id': 10, 'rut': '10.345.678-K', 'first_name': 'Claudia', 'last_name': 'Thomas', 'birth_date': date(1983, 10, 30), 'start_date': date(2016, 7, 3), 'phone': '555-2324', 'email': 'claudia.thomas@psyonix.com', 'salary': 1900.00, 'nationality': 'Spanish', 'active_employee': False, 'afp_id': 3, 'health_plan_id': 7},
    {'id': 11, 'rut': '12.987.654-3', 'first_name': 'Jean', 'last_name': 'Baptiste', 'birth_date': date(1990, 3, 18), 'start_date': date(2021, 7, 12), 'phone': '555-3456', 'email': 'jean.baptiste@psyonix.com', 'salary': 2100.00, 'nationality': 'Haitian', 'active_employee': True, 'afp_id': 4, 'health_plan_id': 8},
    {'id': 12, 'rut': '19.877.654-4', 'first_name': 'Lucas', 'last_name': 'Rodriguez', 'birth_date': date(1994, 4, 2), 'start_date': date(2022, 1, 20), 'phone': '555-9999', 'email': 'lucas.rodriguez@psyonix.com', 'salary': 2400.00, 'nationality': 'Argentine', 'active_employee': True, 'afp_id': 5, 'health_plan_id': 9},
    {'id': 13, 'rut': '11.777.111-5', 'first_name': 'Sofia', 'last_name': 'Martinez', 'birth_date': date(1998, 12, 16), 'start_date': date(2023, 7, 5), 'phone': '555-1111', 'email': 'sofia.martinez@psyonix.com', 'salary': 2100.00, 'nationality': 'Chilean', 'active_employee': False, 'afp_id': 1, 'health_plan_id': 10},
    {'id': 14, 'rut': '20.555.666-7', 'first_name': 'Ariane', 'last_name': 'Dupont', 'birth_date': date(1989, 5, 9), 'start_date': date(2020, 5, 10), 'phone': '555-5555', 'email': 'ariane.dupont@psyonix.com', 'salary': 2800.00, 'nationality': 'French', 'active_employee': False, 'afp_id': 2, 'health_plan_id': 11},
    {'id': 15, 'rut': '17.876.543-8', 'first_name': 'Hiroshi', 'last_name': 'Tanaka', 'birth_date': date(1992, 10, 21), 'start_date': date(2019, 2, 13), 'phone': '555-8888', 'email': 'hiroshi.tanaka@psyonix.com', 'salary': 2500.00, 'nationality': 'Japanese', 'active_employee': True, 'afp_id': 3, 'health_plan_id': 12},
    {'id': 16, 'rut': '13.111.222-3', 'first_name': 'Maya', 'last_name': 'Singh', 'birth_date': date(1986, 8, 14), 'start_date': date(2017, 12, 5), 'phone': '555-7777', 'email': 'maya.singh@psyonix.com', 'salary': 2000.00, 'nationality': 'Indian', 'active_employee': True, 'afp_id': 6, 'health_plan_id': 13}
 ]


for data in employee_data:
    employee = Employee(**data)
    session.add(employee)
session.commit()

# Insert data into Department table
department_data = [
    {'id': 1, 'name': 'Development', 'description': 'Responsible for all technical aspects of game creation, including programming and software development.'},
    {'id': 2, 'name': 'Design', 'description': 'Creates gameplay mechanics, levels, user interfaces, and the overall player experience.'},
    {'id': 3, 'name': 'Art', 'description': 'Responsible for the visual aspects of the game, including 3D modeling, textures, animations, and visual effects.'},
    {'id': 4, 'name': 'Marketing', 'description': 'Handles promotion, community engagement, player feedback, and in-game monetization.'},
    {'id': 5, 'name': 'Quality Assurance (QA)', 'description': 'Ensures the game is bug-free, plays smoothly, and meets quality standards before release.'},
    {'id': 6, 'name': 'Operations', 'description': 'Manages game servers, backend infrastructure, and the deployment of online multiplayer features.'}
]

for data in department_data:
    department = Department(**data)
    session.add(department)
session.commit()

# Insert data into JobPosition table
job_position_data = [
    {'id': 1, 'name': 'Software Engineer', 'description': 'Develops and maintains software applications.', 'department_id': 1},  # Development
    {'id': 2, 'name': 'HR Specialist', 'description': 'Handles employee relations and recruitment.', 'department_id': 2},  # Design (Could be general HR role)
    {'id': 3, 'name': 'Project Manager', 'description': 'Leads and manages project execution.', 'department_id': 1},  # Development
    {'id': 4, 'name': 'System Administrator', 'description': 'Manages IT systems and infrastructure.', 'department_id': 1},  # Development (Operations)
    {'id': 5, 'name': 'Marketing Analyst', 'description': 'Analyzes marketing data and trends.', 'department_id': 4},  # Marketing
    
    # Game Development-focused positions
    {'id': 6, 'name': 'Game Designer', 'description': 'Designs gameplay mechanics, rules, and features to enhance player experience.', 'department_id': 2},  # Design
    {'id': 7, 'name': 'Level Designer', 'description': 'Creates engaging and immersive levels within the game.', 'department_id': 2},  # Design
    {'id': 8, 'name': 'Gameplay Programmer', 'description': 'Develops the core gameplay systems, mechanics, and interactions for the game.', 'department_id': 1},  # Development
    {'id': 9, 'name': '3D Artist', 'description': 'Creates 3D models, textures, and animations for game environments and characters.', 'department_id': 3},  # Art
    {'id': 10, 'name': 'Sound Designer', 'description': 'Responsible for creating and implementing sound effects, music, and voiceovers.', 'department_id': 3},  # Art
    {'id': 11, 'name': 'UI/UX Designer', 'description': 'Designs and optimizes user interfaces and user experiences for the game.', 'department_id': 2},  # Design
    {'id': 12, 'name': 'Game Writer', 'description': 'Creates the story, dialogue, and world-building elements for the game.', 'department_id': 2},  # Design
    {'id': 13, 'name': 'Animation Lead', 'description': 'Leads the animation team in creating character and environment animations for the game.', 'department_id': 3},  # Art
    {'id': 14, 'name': 'QA Tester', 'description': 'Tests the game for bugs, performance issues, and user experience improvements.', 'department_id': 5},  # QA
    {'id': 15, 'name': 'Community Manager', 'description': 'Engages with the game community through social media, events, and feedback channels.', 'department_id': 4},  # Marketing
    {'id': 16, 'name': 'Monetization Specialist', 'description': 'Designs and implements in-game purchasing strategies and monetization features.', 'department_id': 4},  # Marketing
    {'id': 17, 'name': 'Backend Developer', 'description': 'Develops and maintains server-side infrastructure for online multiplayer features.', 'department_id': 6},  # Operations
    {'id': 18, 'name': 'DevOps Engineer', 'description': 'Manages the deployment, automation, and monitoring of game servers and cloud services.', 'department_id': 6},  # Operations
    {'id': 19, 'name': 'Technical Artist', 'description': 'Bridges the gap between art and programming by ensuring that artwork is optimized for the game engine.', 'department_id': 3},  # Art
    {'id': 20, 'name': 'Marketing Director', 'description': 'Leads marketing strategies and campaigns to promote the game.', 'department_id': 4}  # Marketing
]


for data in job_position_data:
    job_position = JobPosition(**data)
    session.add(job_position)
session.commit()

employee_position_data = [
    {'employee_id': 1, 'position_id': 7},  # John -> Game Developer
    {'employee_id': 2, 'position_id': 6},  # Mary -> Talent Acquisition Manager
    {'employee_id': 3, 'position_id': 8},  # Carlos -> Gameplay Programmer
    {'employee_id': 4, 'position_id': 9},  # Anna -> Game Designer
    {'employee_id': 5, 'position_id': 3},  # Louis -> Project Manager
    {'employee_id': 6, 'position_id': 4},  # Laura -> System Administrator
    {'employee_id': 7, 'position_id': 11}, # Robert -> IT Support Specialist
    {'employee_id': 8, 'position_id': 5},  # Fernanda -> UI/UX Designer
    {'employee_id': 9, 'position_id': 5},  # George -> UI/UX Designer
    {'employee_id': 10, 'position_id': 10},  # Claudia -> Technical Artist
    {'employee_id': 11, 'position_id': 12},  # Jean -> Quality Assurance Tester
    {'employee_id': 12, 'position_id': 2},  # Lucas -> 3D Artist
    {'employee_id': 13, 'position_id': 1},  # Sofia -> Game Writer
    {'employee_id': 14, 'position_id': 13},  # Ariane -> Animation Lead
    {'employee_id': 15, 'position_id': 14},  # Hiroshi -> DevOps Engineer
    {'employee_id': 16, 'position_id': 15},  # Maya -> Community Manager
]

for data in employee_position_data:
    emp_pos = EmployeePosition(**data)
    session.add(emp_pos)
session.commit()






# Insert data into Contract table
contract_data = [
    {'id': 1, 'employee_id': 1, 'contract_type': 'Permanent', 'start_date': date(2023, 1, 15), 'end_date': None, 'classification': 'Professional', 'registration_date': date(2020, 1, 15)},
    {'id': 2, 'employee_id': 2, 'contract_type': 'Fixed', 'start_date': date(2019, 3, 10), 'end_date': date(2025, 3, 10), 'classification': 'Administrative', 'registration_date': date(2019, 3, 10)},
    {'id': 3, 'employee_id': 3, 'contract_type': 'Temporary', 'start_date': date(2021, 6, 5), 'end_date': date(2022, 6, 5), 'classification': 'Technical', 'registration_date': date(2021, 6, 5)},
    {'id': 4, 'employee_id': 4, 'contract_type': 'Substitute', 'start_date': date(2018, 9, 25), 'end_date': date(2021, 9, 25), 'classification': 'Auxiliary', 'registration_date': date(2018, 9, 25)},
    {'id': 5, 'employee_id': 5, 'contract_type': 'Permanent', 'start_date': date(2022, 2, 1), 'end_date': None, 'classification': 'Executive', 'registration_date': date(2022, 2, 1)},
    {'id': 6, 'employee_id': 6, 'contract_type': 'Fixed', 'start_date': date(2020, 8, 14), 'end_date': date(2025, 8, 14), 'classification': 'Professional', 'registration_date': date(2020, 8, 14)},
    {'id': 7, 'employee_id': 7, 'contract_type': 'Temporary', 'start_date': date(2017, 10, 12), 'end_date': date(2020, 10, 12), 'classification': 'Technical', 'registration_date': date(2017, 10, 12)},
    {'id': 8, 'employee_id': 8, 'contract_type': 'Permanent', 'start_date': date(2021, 4, 8), 'end_date': None, 'classification': 'Administrative', 'registration_date': date(2021, 4, 8)},
    {'id': 9, 'employee_id': 9, 'contract_type': 'Substitute', 'start_date': date(2020, 3, 14), 'end_date': date(2022, 3, 14), 'classification': 'Executive', 'registration_date': date(2020, 3, 14)},
    {'id': 10, 'employee_id': 10, 'contract_type': 'Fixed', 'start_date': date(2016, 7, 3), 'end_date': date(2019, 7, 3), 'classification': 'Professional', 'registration_date': date(2016, 7, 3)},
    {'id': 11, 'employee_id': 11, 'contract_type': 'Permanent', 'start_date': date(2021, 7, 12), 'end_date': None, 'classification': 'Auxiliary', 'registration_date': date(2021, 7, 12)},
    {'id': 12, 'employee_id': 12, 'contract_type': 'Fixed', 'start_date': date(2021, 1, 20), 'end_date': date(2025, 1, 20), 'classification': 'Technical', 'registration_date': date(2021, 1, 20)},
    {'id': 13, 'employee_id': 13, 'contract_type': 'Temporary', 'start_date': date(2021, 11, 15), 'end_date': date(2022, 11, 15), 'classification': 'Administrative', 'registration_date': date(2021, 11, 15)},
    {'id': 14, 'employee_id': 14, 'contract_type': 'Substitute', 'start_date': date(2022, 5, 1), 'end_date': date(2024, 5, 1), 'classification': 'Executive', 'registration_date': date(2022, 5, 1)},
    {'id': 15, 'employee_id': 15, 'contract_type': 'Permanent', 'start_date': date(2022, 6, 25), 'end_date': None, 'classification': 'Professional', 'registration_date': date(2022, 6, 25)},
    {'id': 16, 'employee_id': 16, 'contract_type': 'Fixed', 'start_date': date(2023, 3, 5), 'end_date': date(2026, 3, 5), 'classification': 'Technical', 'registration_date': date(2023, 3, 5)}
]

for data in contract_data:
    contract = Contract(**data)
    session.add(contract)
session.commit()


# Insert data into Vacation table
vacation_data = [
    {'id': 1, 'employee_id': 1, 'start_date': date(2023, 1, 5), 'end_date': date(2023, 1, 20), 'days_taken': 15, 'accumulated_days': 10, 'long_service_employee': False},
    {'id': 2, 'employee_id': 2, 'start_date': date(2023, 6, 1), 'end_date': date(2023, 6, 10), 'days_taken': 9, 'accumulated_days': 5, 'long_service_employee': False},
    {'id': 3, 'employee_id': 3, 'start_date': date(2022, 12, 15), 'end_date': date(2022, 12, 30), 'days_taken': 15, 'accumulated_days': 3, 'long_service_employee': False},
    {'id': 4, 'employee_id': 4, 'start_date': date(2022, 8, 1), 'end_date': date(2022, 8, 15), 'days_taken': 14, 'accumulated_days': 6, 'long_service_employee': True},
    {'id': 5, 'employee_id': 5, 'start_date': date(2023, 2, 10), 'end_date': date(2023, 2, 25), 'days_taken': 15, 'accumulated_days': 8, 'long_service_employee': False}
]

for data in vacation_data:
    vacation = Vacation(**data)
    session.add(vacation)
session.commit()

# Insert data into Evaluation table
evaluation_data = [
    {'id': 1, 'employee_id': 1, 'evaluation_date': date(2023, 5, 15), 'evaluator': 'Supervisor A', 'evaluation_factor': 6.3, 'rating': 'Good', 'comments': 'Excellent performance.'},
    {'id': 2, 'employee_id': 2, 'evaluation_date': date(2023, 7, 10), 'evaluator': 'Supervisor B', 'evaluation_factor': 5.3, 'rating': 'Satisfactory', 'comments': 'Needs to improve teamwork.'},
    {'id': 3, 'employee_id': 3, 'evaluation_date': date(2023, 3, 25), 'evaluator': 'Supervisor C', 'evaluation_factor': 5.6, 'rating': 'Satisfactory', 'comments': 'Generally good performance.'},
    {'id': 4, 'employee_id': 4, 'evaluation_date': date(2022, 12, 5), 'evaluator': 'Supervisor A', 'evaluation_factor': 6.6, 'rating': 'Very Good', 'comments': 'Highly recommended for promotions.'},
    {'id': 5, 'employee_id': 5, 'evaluation_date': date(2023, 1, 20), 'evaluator': 'Supervisor B', 'evaluation_factor': 4.9, 'rating': 'Fair', 'comments': 'Could improve punctuality.'}
]

for data in evaluation_data:
    evaluation = Evaluation(**data)
    session.add(evaluation)
session.commit()

# Insert data into Training table
training_data = [
    {'id': 1, 'employee_id': 1, 'training_date': date(2023, 3, 5), 'course': 'Advanced Python', 'score': 6.3, 'institution': 'Tech Academy', 'comments': 'Excellent participation.'},
    {'id': 2, 'employee_id': 2, 'training_date': date(2023, 4, 15), 'course': 'Project Management', 'score': 5.6, 'institution': 'University A', 'comments': 'Good grasp of the subject.'},
    {'id': 3, 'employee_id': 3, 'training_date': date(2022, 11, 22), 'course': 'Cybersecurity', 'score': 5.3, 'institution': 'Tech Institute', 'comments': 'Acceptable performance.'},
    {'id': 4, 'employee_id': 4, 'training_date': date(2022, 6, 18), 'course': 'Digital Marketing', 'score': 5.9, 'institution': 'Online Academy', 'comments': 'Good tool mastery.'},
    {'id': 5, 'employee_id': 5, 'training_date': date(2023, 1, 10), 'course': 'Scrum Master', 'score': 4.9, 'institution': 'Scrum Training', 'comments': 'Needs to improve leadership.'}
]

for data in training_data:
    training = Training(**data)
    session.add(training)
session.commit()

# Insert data into Remuneration table
remuneration_data = [
    {'id': 1, 'employee_id': 1, 'afp_id': 7, 'health_plan_id': 1, 'gross_amount': 1800.00, 'tax': 10.0, 'deductions': 150.00, 'bonus': 200.00, 'welfare_contribution': 50.00, 'net_amount': 1400.00},
    {'id': 2, 'employee_id': 2, 'afp_id': 2, 'health_plan_id': 2, 'gross_amount': 3000.00, 'tax': 12.0, 'deductions': 200.00, 'bonus': 250.00, 'welfare_contribution': 60.00, 'net_amount': 2650.00},
    {'id': 3, 'employee_id': 3, 'afp_id': 3, 'health_plan_id': 3, 'gross_amount': 2300.00, 'tax': 9.0, 'deductions': 130.00, 'bonus': 150.00, 'welfare_contribution': 40.00, 'net_amount': 2070.00},
    {'id': 4, 'employee_id': 4, 'afp_id': 4, 'health_plan_id': 1, 'gross_amount': 2800.00, 'tax': 11.0, 'deductions': 180.00, 'bonus': 300.00, 'welfare_contribution': 55.00, 'net_amount': 2455.00},
    {'id': 5, 'employee_id': 5, 'afp_id': 5, 'health_plan_id': 2, 'gross_amount': 2700.00, 'tax': 10.5, 'deductions': 170.00, 'bonus': 280.00, 'welfare_contribution': 50.00, 'net_amount': 2390.00},
    {'id': 6, 'employee_id': 6, 'afp_id': 6, 'health_plan_id': 3, 'gross_amount': 2400.00, 'tax': 9.5, 'deductions': 160.00, 'bonus': 220.00, 'welfare_contribution': 45.00, 'net_amount': 2110.00},
    {'id': 7, 'employee_id': 7, 'afp_id': 7, 'health_plan_id': 4, 'gross_amount': 3100.00, 'tax': 11.5, 'deductions': 250.00, 'bonus': 200.00, 'welfare_contribution': 65.00, 'net_amount': 2735.00},
    {'id': 8, 'employee_id': 8, 'afp_id': 1, 'health_plan_id': 5, 'gross_amount': 2600.00, 'tax': 10.0, 'deductions': 140.00, 'bonus': 230.00, 'welfare_contribution': 50.00, 'net_amount': 2380.00},
    {'id': 9, 'employee_id': 9, 'afp_id': 2, 'health_plan_id': 6, 'gross_amount': 2900.00, 'tax': 12.0, 'deductions': 210.00, 'bonus': 270.00, 'welfare_contribution': 55.00, 'net_amount': 2415.00},
    {'id': 10, 'employee_id': 10, 'afp_id': 3, 'health_plan_id': 7, 'gross_amount': 2200.00, 'tax': 9.0, 'deductions': 120.00, 'bonus': 180.00, 'welfare_contribution': 40.00, 'net_amount': 1940.00},
    {'id': 11, 'employee_id': 11, 'afp_id': 4, 'health_plan_id': 8, 'gross_amount': 2500.00, 'tax': 10.5, 'deductions': 150.00, 'bonus': 210.00, 'welfare_contribution': 50.00, 'net_amount': 2200.00},
    {'id': 12, 'employee_id': 12, 'afp_id': 5, 'health_plan_id': 9, 'gross_amount': 3000.00, 'tax': 11.0, 'deductions': 190.00, 'bonus': 250.00, 'welfare_contribution': 60.00, 'net_amount': 2700.00},
    {'id': 13, 'employee_id': 13, 'afp_id': 1, 'health_plan_id': 10, 'gross_amount': 2800.00, 'tax': 10.5, 'deductions': 180.00, 'bonus': 240.00, 'welfare_contribution': 55.00, 'net_amount': 2505.00},
    {'id': 14, 'employee_id': 14, 'afp_id': 2, 'health_plan_id': 11, 'gross_amount': 3200.00, 'tax': 12.0, 'deductions': 210.00, 'bonus': 290.00, 'welfare_contribution': 70.00, 'net_amount': 2890.00},
    {'id': 15, 'employee_id': 15, 'afp_id': 3, 'health_plan_id': 12, 'gross_amount': 3000.00, 'tax': 10.0, 'deductions': 200.00, 'bonus': 300.00, 'welfare_contribution': 60.00, 'net_amount': 2740.00},
    {'id': 16, 'employee_id': 16, 'afp_id': 4, 'health_plan_id': 13, 'gross_amount': 3400.00, 'tax': 13.0, 'deductions': 220.00, 'bonus': 310.00, 'welfare_contribution': 75.00, 'net_amount': 3180.00}
]

for data in remuneration_data:
    remuneration = Remuneration(**data)
    session.add(remuneration)
session.commit()

# Close the session
session.close()
