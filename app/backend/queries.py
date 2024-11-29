import os
from decimal import Decimal
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
from tables import *

# Load the MySQL root password from environment variables
# mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {
    'host': 'mysql',
    'database_name': 'hr',
    'user': 'root',
    'password': 'a301rrhh' 
    }

# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
engine = create_engine('mysql+pymysql://root:a301rrhh@mysql:3306/hr')
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

# MENU Queries ------------------------------------------------------------------------------------------------|
def all_afps(session):
    """Retrieve all afps and their data."""
    try:
        afps = session.query(AFP).all()
        return [
            {
                'id': afp.id,
                'name': afp.name,
                'commission_percentage': afp.commission_percentage,
            }
            for afp in afps
        ]
    except Exception as e:
        print(f'Error in all_companies: {e}')
    return []

def all_health_plans(session):
    """Retrieve all health plans with their respective discounts."""
    try:
        # Query HealthPlan, Fonasa, and Isapre
        health_plans = session.query(HealthPlan, Fonasa, Isapre). \
            outerjoin(Fonasa, HealthPlan.id == Fonasa.health_plan_id). \
            outerjoin(Isapre, HealthPlan.id == Isapre.health_plan_id). \
            all()

        return [
            {
                'health_plan_id': health_plan.id,
                'name': health_plan.name,
                'type': health_plan.type,
                'fonasa_discount': fonasa.discount if fonasa else None,
                'isapre_discount': isapre.discount if isapre else None,
            }
            for health_plan, fonasa, isapre in health_plans
        ]
    except Exception as e:
        print(f'Error in all_health_plans: {e}')
    return []

def all_companies(session):
    """Retrieve all companies and their data."""
    try:
        companies = session.query(Company).all()
        return [
            {
                'rut': company.rut,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'industry': company.industry
            }
            for company in companies
        ]
    except Exception as e:
        print(f'Error in all_companies: {e}')
    return []


# EMPLOYEE Queries ------------------------------------------------------------------------------------------------|
def search_employee_by_name_or_rut(search_query, session):
    """Search an employee by name or RUT with flexible matching."""
    search_terms = search_query.split()
    if len(search_terms) == 1:
        term = f"%{search_terms[0]}%"
        result = session.query(Employee).filter(
            (Employee.first_name.like(term)) | 
            (Employee.last_name.like(term)) | 
            (Employee.rut == search_query)
        ).first()
    elif len(search_terms) == 2:
        result = session.query(Employee).filter(
            (Employee.first_name.like(f"%{search_terms[0]}%")) &
            (Employee.last_name.like(f"%{search_terms[1]}%"))
        ).first()
    else:
        result = None
    return result

def aditional_info(session, employee_id):
    """Get additional information about an employee including net amount, health plan, nationality, birth date, start date, salary, and AFP."""
    try:
        info = session.query(
            Employee.nationality,
            Employee.birth_date,
            Employee.start_date,
            Employee.salary,
            Remuneration.net_amount,
            HealthPlan.name.label('health_plan'),
            AFP.name.label('afp_name')
        ).select_from(Employee) \
        .outerjoin(Remuneration, Employee.id == Remuneration.employee_id) \
        .outerjoin(HealthPlan, Remuneration.health_plan_id == HealthPlan.id) \
        .outerjoin(AFP, Remuneration.afp_id == AFP.id) \
        .filter(Employee.id == employee_id).first()  # Changed to first()

        if info:
            today = datetime.today().date()
            age = (today.year - info[1].year) if info[1] else None
            days_since_start = (today - info[2]).days if info[2] else None
            net_amount = int(info[4]) if isinstance(info[4], Decimal) else info[4]

            return {
                'nationality': info[0],
                'birth_date': info[1],
                'age': age,
                'start_date': info[2],
                'days_since_start': days_since_start,
                'salary': info[3],
                'net_amount': net_amount,
                'health_plan': info[5] or "No health plan registered",
                'afp_name': info[6] or "No AFP registered"
            }
    except Exception as e:
        print(f'Error in aditional_info: {e}')
    return None

def general_info(session, employee_id):
    """Get basic information about an employee."""
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.email, Employee.phone, Employee.rut, JobPosition.name, Employee.active_employee) \
            .outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
            .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id) \
            .filter(Employee.id == employee_id).first()
        return info
    except Exception as e:
        print(f'Error in general_info: {e}')
    return None

def get_filtered_employees(session, job_position_id=None, department_id=None, status=None):
    """Get employees filtered by job position and/or department."""
    query = (
        session.query(Employee.id, Employee.rut, Employee.first_name, Employee.last_name, JobPosition.name.label('position_name'), Department.name.label('department_name'))
        .outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id)
        .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id)
        .outerjoin(Department, JobPosition.department_id == Department.id)
    )

    # Apply filters if provided
    if job_position_id:
        query = query.filter(JobPosition.id == job_position_id)
    if department_id:
        query = query.filter(Department.id == department_id)
    if status:
        query = query.filter(Employee.active_employee == status)

    
    return [
        {
            "id": emp.id,
            "rut": emp.rut,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "position": emp.position_name or "No Position",
            "department": emp.department_name or "No Department",
        }
        for emp in query.all()
    ]

def get_employees_by_department(department_id):
    """
    Fetches all employees who are in positions within a given department.
    """
    # Query the employees through the JobPosition and Department relationship
    employees = session.query(Employee).join(EmployeePosition).join(JobPosition).filter(JobPosition.department_id == department_id).all()

    return employees

def get_employee_name_by_rut(employee_rut):
    """Fetch employee name by RUT"""
    session = Session()
    try:
        employee = session.query(Employee).filter_by(rut=employee_rut).first()
        if employee:
            return employee.first_name + ' ' + employee.last_name
        else:
            return None
    finally:
        session.close()


def get_employee_id_by_rut(session, rut):
    """Get the employee ID by RUT."""
    try:
        employee = session.query(Employee.id).filter_by(rut=rut).first()
        return employee.id if employee else None
    except Exception as e:
        print(f'Error in get_employee_id_by_rut: {e}')
        return None

def all_employees(session):
    """Retrieve all employees with their rut, first name, last name, position, and department"""
    try:
        query = session.query(
            Employee.id, Employee.rut, Employee.first_name, Employee.last_name,
            JobPosition.name.label('position_name'), Department.name.label('department_name')
        ).outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
         .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id) \
         .outerjoin(Department, JobPosition.department_id == Department.id)
        return [
            {
                "id": row.id,
                "rut": row.rut,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "position": row.position_name or "No Position",
                "department": row.department_name or "No Department",
            }
            for row in query.all()
        ]
    except Exception as e:
        print(f'Error in all_employees: {e}')
    return []


#OTHER Queries ------------------------------------------------------------------------------------------------|
def get_job_positions(session):
    """Get all job positions."""
    return session.query(JobPosition).all()

def get_departments(session):
    """Get all departments."""
    return session.query(Department).all()

def department_info(department_id):
    """
    Fetches department name and description by department ID.
    """
    department = session.query(Department).filter(Department.id == department_id).first()

    if department:
        return department.name, department.description
    return None


def get_all_evaluations(session):
    """Get all evaluations with employee details."""
    evaluations = session.query(Evaluation, Employee).join(Employee, Evaluation.employee_id == Employee.id).all()
    return [
        {
            'evaluation_date': eval.evaluation_date,
            'evaluator': eval.evaluator,
            'evaluation_factor': eval.evaluation_factor,
            'rating': eval.rating,
            'comments': eval.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"
        }
        for eval, employee in evaluations
    ]

def get_all_trainings(session):
    """Get all trainings with employee details."""
    trainings = session.query(Training, Employee).join(Employee, Training.employee_id == Employee.id).all()
    return [
        {
            'training_date': train.training_date,
            'course': train.course,
            'score': train.score,
            'institution': train.institution,
            'comments': train.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"  # Add employee's full name
        }
        for train, employee in trainings
    ]

def all_vacations(session):
    """Retrieve all vacations and their employee data."""
    try:
        vacations = (session.query(Vacation, Employee).join(Employee, Vacation.employee_id == Employee.id).all())
        return [
            {
                'id': vacation.id,
                'employee': f"{employee.first_name} {employee.last_name}",
                'start_date': vacation.start_date,
                'end_date': vacation.end_date,
                'days_taken': vacation.days_taken,
                'accumulated_days': vacation.accumulated_days,
                'long_service_employee': vacation.long_service_employee,
            }
            for vacation, employee in vacations
        ]
    except Exception as e:
        print(f'Error in all_vacations: {e}')
    return []

def all_remunerations(session):
    """Retrieve all remunerations and their related employee, AFP, and health plan data."""
    try:
        remunerations = (
            session.query(Remuneration, Employee, AFP, HealthPlan)
            .join(Employee, Remuneration.employee_id == Employee.id)
            .join(AFP, Remuneration.afp_id == AFP.id)
            .join(HealthPlan, Remuneration.health_plan_id == HealthPlan.id)
            .all()
        )
        return [
            {
                'id': remuneration.id,
                'employee': f"{employee.first_name} {employee.last_name}",
                'afp': afp.name,
                'health_plan': health_plan.name,
                'gross_amount': remuneration.gross_amount,
                'tax': remuneration.tax,
                'deductions': remuneration.deductions,
                'bonus': remuneration.bonus,
                'welfare_contribution': remuneration.welfare_contribution,
                'net_amount': remuneration.net_amount,
            }
            for remuneration, employee, afp, health_plan in remunerations
        ]
    except Exception as e:
        print(f'Error in all_remunerations: {e}')
    return []


# CONTRACT Queries
def get_contract_by_employee_id(session, employee_id):
    """Get the contract associated with a specific employee."""
    try:
        contract = session.query(Contract).filter_by(employee_id=employee_id).first()
        return contract
    except SQLAlchemyError as e:
        print(f'Error retrieving contract for employee {employee_id}: {e}')
        return None

def all_contracts(session):
    """Retrieve all contracts and their employee data."""
    try:
        contracts = session.query(Contract, Employee, JobPosition) \
            .join(Employee, Contract.employee_id == Employee.id) \
            .join(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
            .join(JobPosition, EmployeePosition.position_id == JobPosition.id) \
            .all()
        
        return [
            {
                'id': contract.id,
                'employee': f"{employee.first_name} {employee.last_name}",
                'contract_type': contract.contract_type,
                'start_date': contract.start_date,
                'end_date': contract.end_date,
                'classification': contract.classification,
                'position': position.name,
                'registration_date': contract.registration_date,
            }
            for contract, employee, position in contracts
        ]
    except Exception as e:
        print(f'Error in all_contracts: {e}')
    return []

def get_contract_info(session, employee_id):
    try:
        contract = session.query(Contract.contract_type, Contract.start_date, 
                             Contract.end_date, Contract.classification, 
                             Contract.registration_date, JobPosition.name) \
                            .join(Employee, Contract.employee_id == Employee.id) \
                            .join(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
                            .join(JobPosition, EmployeePosition.position_id == JobPosition.id) \
                            .filter(Contract.employee_id==employee_id) \
                            .order_by(Contract.start_date.desc()).first()
        return contract
    except Exception as e:
        print(f'Error in general_info: {e}')
    return None