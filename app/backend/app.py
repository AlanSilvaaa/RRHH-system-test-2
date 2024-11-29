import os
from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *
from interactions import *

app = Flask(
    __name__, 
    template_folder=os.path.join('/app/frontend/src/templates'),
    static_folder=os.path.join('/app/frontend/src/static')
)
app.secret_key = 'magickey'


# Route for menu page (homepage)
@app.route('/')
def homepage():
    job_position_id = request.args.get('job_position', type=int)
    department_id = request.args.get('department', type=int)
    status = request.args.get('status', 1) # Default status is 1 (active)

    # Get filtered employees
    employees = get_filtered_employees(session, job_position_id, department_id, status)
    
    # Fetch job positions and departments for dropdown lists
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    return render_template('index.html', employees=employees, job_positions=job_positions, departments=departments)


# Route for employee profile with integrated search
@app.route('/employee')
def user():
    search_query = request.args.get('search_query')
    
    # Perform the search if there is a search parameter
    if search_query:
        employee = search_employee_by_name_or_rut(search_query, session)
        
        # Redirect to profile if an employee is found
        if employee:
            return redirect(url_for('user', id=employee.id))  # Change here to ensure redirection with ?id

        # Show error message if the employee is not found
        return render_template('index.html', error_message="Employee not found")
    
    # Get the employee ID if there is no search parameter
    employee_id = request.args.get('id')

    if not employee_id:
        # Show message if no employee_id is provided
        return render_template('employee.html', error_message="No employee ID provided")

    # Get employee information
    gi = general_info(session, employee_id)
    ad_info = aditional_info(session, employee_id)

    # Check if general information is missing
    if not gi:
        return render_template('employee.html', error_message="Employee not found")

    # Get the current contract
    contract = get_contract_info(session, employee_id)
    
    # Order the data to be passed to the template
    contract_data = {
        'contract_type': contract.contract_type,
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'classification': contract.classification,
        'position': contract.name, # it's actually not the name of the contract, but the name of the JobPosition
        'registration_date': contract.registration_date
    } if contract else None

    # Employee data
    first_name, last_name, email, phone, rut, position, status = gi

    # Change employee status to "Active" or "Inactive"
    if status == 0:
        status = "Inactive"
    elif status == 1:
        status = "Active"
    else:
        status = "Unknown"

    # Show missing information
    missing_info = []
    if not ad_info:
        missing_info.append("No additional info available")
    if not ad_info.get('net_amount'):
        missing_info.append("No net amount registered")
    if ad_info.get('health_plan') == "No health plan registered":
        missing_info.append("No health plan registered")

    # Get job positions and departments
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    # Pass the data to the template, including the current contract and job_positions and departments
    return render_template(
        'employee.html',
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        rut=rut,
        position=position,
        status=status,
        nationality=ad_info.get('nationality', "Not registered"),
        birth_date=ad_info.get('birth_date', "Not registered"),
        age=ad_info.get('age', "Not available"),
        start_date=ad_info.get('start_date', "Not registered"),
        days_since_start=ad_info.get('days_since_start', "Not available"),
        salary=ad_info.get('salary', "Not registered"),
        net_amount=ad_info.get('net_amount', "Not registered"),
        health_plan=ad_info.get('health_plan', "Not registered"),
        afp_name=ad_info.get('afp_name', "Not registered"),
        missing_info=missing_info,
        contract=contract_data,
        job_positions=job_positions,  # Pass job positions
        departments=departments       # Pass departments
    )


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Collect form data
        employee_data = {
            'rut': request.form['rut'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birth_date': request.form['birth_date'],
            'start_date': request.form['start_date'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'salary': request.form['salary'],
            'nationality': request.form['nationality'].capitalize(),
            'afp': request.form['afp_id'],
            'healthplan': request.form['healthplan_id'],
        }

        # Call the function to add the employee
        result = add_employee_to_db(session, employee_data)
        flash(result)
        return redirect(url_for('homepage'))
    
    afps = all_afps(session)

    healthplans = all_health_plans(session)
    
    return render_template('add_employee.html', afps=afps, healthplans=healthplans)

    # Get job positions to display in the form
    job_positions = get_job_positions(session)
    return render_template('add_employee.html', job_positions=job_positions)

@app.route("/edit_employee", methods=['GET', 'POST'])
def edit_employee():
    employee_id = request.args.get('id')
    
    if request.method == 'POST':
        data = {
            'employee_id': int(request.form['employee_id']),
            'first_name': request.form['First Name'],
            'last_name': request.form['Last Name'],
            'email': request.form['Email'],
            'phone': request.form['Phone'],
            'rut': request.form['RUT'],
        }
        # make query to update the values
        print("this should be the employee id", data['employee_id'])
        update_employee(session, data)
        return redirect(url_for('homepage'))
    
    gi = general_info(session, employee_id)
    labels = ['First Name', 'Last Name', 'Email', 'Phone', 'RUT', 'Position', 'Status']
    gi_data = {}
    for i in range(len(labels)):
        gi_data[labels[i]] = gi[i]
    
    # NOTE:
    # It isn't necessary to make a dictionary with labels to aditional info because it is already 
    # defined as a dict with labels, unlike general_info, which is only defined as an array
    ad_info = aditional_info(session, employee_id)
    for key, value in ad_info.items():
        print(key, value)
    return render_template('edit_employee.html', gi_data=gi_data, ad_info_data=ad_info, employee_id=employee_id)

@app.route('/disable_employee/<int:employee_id>')
def disable_employee(employee_id):
    # Logic to load the information of the contract to be deleted
    employee = Employee.query.get(employee_id)
    return render_template('disable_employee.html', employee=employee)


@app.route('/confirm_disable_employee/<int:employee_id>', methods=['POST'])
def confirm_disable_employee(employee_id):
    # Get the contract using the custom query function
    contract_deactivated = deactivate_employee(session, employee_id)

    # Show success or error message
    if contract_deactivated:
        flash('Contract successfully deactivated', 'success')
    else:
        flash('Error: Contract could not be deactivated', 'danger')

    return redirect(url_for('user', id=employee_id))

# MENU PAGES ------------------------------------------------------------------------------------------------|

@app.route('/afps')
def show_afps():
    with Session() as session:
        afps = all_afps(session)
    return render_template('afps.html', afps=afps)


@app.route('/companies')
def show_companies():
    with Session() as session:
        companies = all_companies(session)
    return render_template('companies.html', companies=companies)

@app.route('/add_company', methods=['GET', 'POST']) 
def add_company():
    if request.method == 'POST':
        # Gather form data
        company_data = {
            'rut': request.form['rut'],
            'name': request.form['name'],
            'address': request.form['address'],
            'phone': request.form['phone'],
            'industry': request.form['industry'].capitalize(),
        }

        # Call the function to add the company
        result = add_company_to_db(session, company_data)
        flash(result)
        return redirect(url_for('show_companies'))  # Redirect to homepage or appropriate view

    # Fetch job positions and departments for the form (if needed)
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    # Render the form for GET requests
    return render_template('add_company.html', job_positions=job_positions, departments=departments)



@app.route('/health_plans')
def health_plans():
    session = Session()

    # Get all health plans with their discounts
    health_plans = all_health_plans(session)

    # Return the template with the health plans data
    return render_template('health_plans.html', health_plans=health_plans)

# TOPBAR PAGES ------------------------------------------------------------------------------------------------|

@app.route('/remuneration')
def remunerations_page():
    session = Session()
    remuneration = all_remunerations(session)
    session.close()
    return render_template('remunerations.html', remunerations=remuneration)

@app.route('/add_remuneration', methods=['GET', 'POST'])
def add_remuneration_page():
    if request.method == 'POST':
        with Session() as session:
            remuneration_data = {
                'employee_id': get_employee_id_by_rut(session,request.form['employee_rut']),
                'afp_id': request.form['afp_id'],
                'healthplan_id': request.form['healthplan_id'],
                'gross_amount': request.form['gross_amount'],
                'tax': request.form['tax'],
                'welfare_contribution': request.form['welfare_contribution'],
            }
            result = add_remuneration(session, remuneration_data)
            flash(result)

    
    session = Session()
    afps = session.query(AFP).all()
    healthplans = session.query(HealthPlan).all()
    
    return render_template('add_remuneration.html', afps=afps, healthplans=healthplans)

@app.route('/contracts')
def show_contracts():
    with Session() as session:
        contracts = all_contracts(session)
    return render_template('contracts.html', contracts=contracts)

# Route for the option of adding a new "Contract"
@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract_page():
    if request.method == 'POST':
        session = Session()

        contract_data = {
            'employee_id': get_employee_id_by_rut(session, request.form.get('employee_rut')),  
            'contract_type': request.form.get('contract_type'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'classification': request.form.get('classification'),
            'job_position': request.form.get('job_position'),
            'department': request.form.get('department')
        }

        # Validate that required fields are present
        required_fields = ['employee_id', 'contract_type', 'start_date', 'job_position', 'department']
        missing_fields = [field for field in required_fields if not contract_data.get(field)]
        
        if missing_fields:
            flash(f"Error: Missing fields: {', '.join(missing_fields)}", 'danger')
            return redirect(url_for('add_contract_page'))

        # Try to add the contract
        try:
            message = add_contract(session, contract_data)
            flash(message, 'success')
            return redirect(url_for('show_contracts'))  # Redirect to contracts page
        except Exception as e:
            session.rollback()
            flash(f"Error adding contract: {e}", 'danger')
        finally:
            session.close()
    
    # Prepare data for the form
    with Session() as session:
        employees = session.query(Employee).all()
        job_positions = get_job_positions(session)
        departments = get_departments(session)
    return render_template(
        'add_contract.html', 
        employees=employees,
        job_positions=job_positions,
        departments=departments
    )


@app.route('/vacations')
def show_vacations():
    with Session() as session:
        vacations = all_vacations(session)
    return render_template('vacations.html', vacations=vacations)


# Route for adding vacation (no database interaction)
@app.route('/add_vacation', methods=['GET', 'POST'])
def add_vacation():
    with Session() as session:
        if request.method == 'POST':
            
            # Get form data
            vacation_data = {
                'employee_id': get_employee_id_by_rut(session, request.form.get('employee_rut')),
                'start_date': request.form['start_date'],
                'end_date': request.form['end_date'],
                'days_taken': int(request.form['days_taken']),  # Convert to int
                'accumulated_days': int(request.form['accumulated_days']),  # Convert to int
                'long_service_employee': request.form.get('long_service_employee', False)
            }


            # Convert checkbox value to boolean
            vacation_data['long_service_employee'] = vacation_data['long_service_employee'] == "on"

            # Call the query function
            message = add_vacation_to_db(session, vacation_data)

            # Provide feedback to the user
            flash(message)
            return redirect(url_for('show_vacations'))

    return render_template('add_vacation.html')



@app.route('/train_eval')
def eval_train():
    with Session() as session:
        evaluations = get_all_evaluations(session)
        trainings = get_all_trainings(session)
    return render_template('train_eval.html', evaluations=evaluations, trainings=trainings)

@app.route('/add_evaluation', methods=['GET', 'POST'])
def handle_add_evaluation():
    if request.method == 'POST':
        session = Session()
        evaluation_data = {
            'employee_id': get_employee_id_by_rut(session, request.form.get('employee_rut')),
            'evaluation_date': request.form['evaluation_date'],
            'evaluator': request.form['evaluator'],
            'evaluation_factor': request.form['evaluation_factor'],
            'rating': request.form['rating'],
            'comments': request.form['comments']
        }
        session = Session()
        result = add_evaluation(session, evaluation_data)
        flash(result)

        return redirect(url_for('eval_train'))
    
    return render_template('add_eval.html')

@app.route('/add_training', methods=['GET', 'POST'])
def handle_add_training():
    if request.method == 'POST':
        session = Session()
        training_data = {
            'employee_id': get_employee_id_by_rut(session, request.form.get('employee_rut')),
            'training_date': request.form['training_date'],
            'course': request.form['course'],
            'score': request.form['score'],
            'institution': request.form['institution'],
            'comments': request.form['comments']
        }
        session = Session()
        result = add_training(session, training_data)
        flash(result)

        return redirect(url_for('eval_train'))
    
    return render_template('add_train.html')

@app.route('/get_employee_name/<string:employee_rut>', methods=['GET'])  # Changed to <string:employee_rut>
def get_employee_name(employee_rut):
    employee_name = get_employee_name_by_rut(employee_rut)  # Call the new function
    if employee_name:
        return employee_name  # Return the name as plain text
    else:
        return "Does not exist", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
