import os
from decimal import Decimal
from sqlalchemy import create_engine, text, func, update
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

# EMPLOYEE Interactions

def add_employee_to_db(session, employee_data):
    """Add an employee to the database."""
    try:
        new_employee = Employee(
            rut=employee_data['rut'],
            first_name=employee_data['first_name'],
            last_name=employee_data['last_name'],
            birth_date=employee_data['birth_date'],
            start_date=employee_data['start_date'],
            email=employee_data['email'],
            phone=employee_data['phone'],
            salary=employee_data['salary'],
            nationality=employee_data['nationality'],
            afp_id=employee_data['afp'],
            health_plan_id=employee_data['healthplan'],
        )
        session.add(new_employee)
        session.commit()
        return "Empleado agregado exitosamente"
    except Exception as e:
        session.rollback()
        return f"Error al agregar el empleado: {e}"

def deactivate_employee(session, employee_id):
    """Deactivate an employee by setting active_employee to False."""
    try:
        employee = session.query(Employee).filter_by(id=employee_id).first()
        if employee:
            employee.active_employee = False
            session.commit()
            return "Employee deactivated successfully."
        return f"Employee with ID {employee_id} not found."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error deactivating employee: {str(e)}"

def update_employee(session, data):
    """Update an employee's information."""
    try:
        # Check if the employee exists
        employee = session.query(Employee).filter(Employee.id == data['employee_id']).first()
        
        if employee:
            # Update the first name
            employee.first_name = data['first_name']
            employee.last_name = data['last_name']
            employee.email = data['email']
            employee.phone = data['phone']
            employee.rut = data['rut']
            session.commit()
            print(f"Employee {data['employee_id']}'s first name updated to '{data['first_name']}'.")
        else:
            print(f"No employee found with ID {data['employee_id']}")
    except Exception as e:
        session.rollback()  # Roll back the session in case of error
        print(f'Error updating employee: {e}')
    finally:
        session.close()
    return None

def add_company_to_db(session, company_data):
    """
    Adds a new company to the database using the provided data.
    """
    try:
        # Create a new Company instance with the provided data
        new_company = Company(
            rut=company_data['rut'],
            name=company_data['name'],
            address=company_data['address'],
            phone=company_data['phone'],
            industry=company_data['industry']
        )
        session.add(new_company)
        session.commit()
        return "Company added successfully"
    except Exception as e:
        session.rollback()
        return f"Error adding company: {e}"

def add_remuneration(session, remuneration_data):
    """Add a remuneration for an employee."""
    try:
        # Fetch the Employee using employee_id
        employee = session.query(Employee).filter_by(id=remuneration_data['employee_id']).first()
        
        if not employee:
            return f"Employee with ID {remuneration_data['employee_id']} not found."
        
        # Auto-complete afp_id and health_plan_id from Employee's AFP and HealthPlan
        remuneration_data['afp_id'] = employee.afp_id
        remuneration_data['health_plan_id'] = employee.health_plan_id

        # Ensure numeric fields are converted to float
        gross_amount = float(remuneration_data.get('gross_amount', 0))
        tax = float(remuneration_data.get('tax', 0))
        deductions = float(remuneration_data.get('deductions', 0))
        bonus = float(remuneration_data.get('bonus', 0))
        welfare_contribution = float(remuneration_data.get('welfare_contribution', 0))
        net_amount = float(remuneration_data.get('net_amount', 0))

        # Create new Remuneration record
        remuneration = Remuneration(
            employee_id=remuneration_data['employee_id'],
            afp_id=remuneration_data['afp_id'],
            health_plan_id=remuneration_data['health_plan_id'],
            gross_amount=gross_amount,
            tax=tax,
            deductions=deductions,
            bonus=bonus,
            welfare_contribution=welfare_contribution,
            net_amount=net_amount
        )

        # Add to session and commit
        session.add(remuneration)
        session.commit()
        return "Remuneration added successfully."

    except SQLAlchemyError as e:
        session.rollback()
        return f"Error adding remuneration: {str(e)}"


def add_contract(session, contract_data):
    """
    Adds a new contract to the database, creating the position and department if they don't exist.
    """

    department_name = contract_data['department']
    position_name = contract_data['job_position']
    employee_id = contract_data['employee_id']
    contract_type = contract_data['contract_type']
    start_date = contract_data['start_date']
    end_date = contract_data['end_date']
    classification = contract_data['classification']

    # Fetch the employee ID using the provided RUT

    try:
        # Check or create department
        department = session.query(Department).filter_by(name=department_name).first()
        if not department:
            department = Department(name=department_name, description=f"Department {department_name}")
            session.add(department)
            session.flush()  # Ensure department ID is available immediately
        
        # Check or create position
        position = session.query(JobPosition).filter_by(name=position_name, department_id=department.id).first()
        if not position:
            position = JobPosition(name=position_name, description=f"Position {position_name}", department_id=department.id)
            session.add(position)
            session.flush()  # Ensure position ID is available immediately

        # Associate position with the employee
        employee_position = session.query(EmployeePosition).filter_by(employee_id=employee_id, position_id=position.id).first()
        if not employee_position:
            employee_position = EmployeePosition(employee_id=employee_id, position_id=position.id)
            session.add(employee_position)
        
        # Create contract
        new_contract = Contract(
            employee_id=employee_id,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            classification=classification,
            registration_date=date.today()
        )
        session.add(new_contract)
        session.commit()
        return {"success": True, "message": "Contract added successfully!"}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": str(e)}


def add_vacation_to_db(session, vacation_data):
    """Adds a vacation for an employee to the database."""
    try:
        # Convert dates from string to date objects
        start_date = datetime.strptime(vacation_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(vacation_data['end_date'], '%Y-%m-%d').date()

        # Validate that start_date is before end_date
        if start_date > end_date:
            return False, "Start date must be before the end date!"

        # Fetch the employee
        employee = session.query(Employee).filter_by(id=vacation_data['employee_id']).first()
        if not employee:
            return False, "Employee not found!"

        # Check if requested vacation exceeds accumulated days
        requested_days = (end_date - start_date).days + 1
        if requested_days > vacation_data['accumulated_days']:
            return False, "Insufficient vacation days!"

        # Update accumulated days
        vacation_data['accumulated_days'] -= requested_days

        # Create a new Vacation entry
        new_vacation = Vacation(
            employee_id=vacation_data['employee_id'],
            start_date=start_date,
            end_date=end_date,
            days_taken=requested_days,
            accumulated_days=vacation_data['accumulated_days'],
            long_service_employee=vacation_data['long_service_employee']
        )
        session.add(new_vacation)
        session.commit()

        return True, "Vacation added successfully!"
    except Exception as e:
        session.rollback()
        return False, str(e)

def add_training(session, training_data):
    """Add a training record."""
    try:
        session.add(Training(**training_data))
        session.commit()
        return "Training added successfully."
    except SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction on error
        return f"Error adding training: {str(e)}"


#OLD
def add_evaluation(session, evaluation_data):
    """Add an evaluation for an employee."""
    try:
        # Get the evaluation factor (numeric grade)
        evaluation_factor = float(evaluation_data.get('evaluation_factor', 0))

        # Add the rating to the evaluation data
        rating = (
             # Determine rating based on the evaluation factor ranges
            "Excellent" if evaluation_factor == 7 else
            "Very Good" if 6.5 <= evaluation_factor < 7 else
            "Good" if 6 <= evaluation_factor < 6.4 else
            "Satisfactory" if 5 <= evaluation_factor < 6 else
            "Fair" if 4 >= evaluation_factor > 5 else "Deficient"
        )
        evaluation_data['rating'] = rating
        session.add(Evaluation(**evaluation_data))
        session.commit()
        return "Evaluation added successfully."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error adding evaluation: {str(e)}"
    
#NEW
def add_evaluation_to_db(session, evaluation_data):
    try:
        new_evaluation = Evaluation(
            employee_id=evaluation_data['employee_id'],
            evaluation_date=evaluation_data['evaluation_date'],
            evaluator=evaluation_data['evaluator'],
            evaluation_factor=evaluation_data['evaluation_factor'],
            rating=evaluation_data['rating'],
            comments=evaluation_data['comments'],
        )
        session.add(new_evaluation)
        session.commit()
        return "Evaluation added successfully"
    except Exception as e:
        session.rollback()
        return f"Error adding evaluation: {e}"



