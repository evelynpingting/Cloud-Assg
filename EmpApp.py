from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('MainMenu.html')


@app.route("/AboutUs", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

# @app.route("/addemp", methods=['POST'])
# def calculate_salary(exp_yr, edu_lvl, position):
    # Set base salaries for each position
    # base_salaries = {'graphic designer': 30000, 'web developer': 50000, 'marketing analyst': 40000,
    #                  'content creator': 35000, 'digital marketing manager': 70000, 'social media manager': 45000}
    
    # base_salary = base_salaries[position]
    # if position == "graphic_designer":
    #     base_salary = 30000
    #     salary = base_salary + (0.05 * base_salary)
    # elif position == "web_developer":
    #     base_salary = 50000
    #     salary = base_salary + (0.1 * base_salary)
    # elif position == "marketing_analyst":
    #     base_salary = 40000
    #     salary = base_salary + (0.2 * base_salary)
    # elif position == "content_creator":
    #     base_salary = 35000
    #     salary = base_salary + (0.3 * base_salary)
    # elif position == "digital_marketing_manager":
    #     base_salary = 70000
    #     salary = base_salary + (0.4 * base_salary)
    # elif position == "social_media_manager":
    #     base_salary = 45000
    #     salary = base_salary + (0.4 * base_salary)
    # else:
    #     raise ValueError("Invalid position")
    
    if position == "graphic designer":
        base_salary = 30000
        salary = base_salary + (0.05 * base_salary)
    elif position == "web developer":
        base_salary = 50000
        salary = base_salary + (0.1 * base_salary)
    elif position == "marketing analyst":
        base_salary = 40000
        salary = base_salary + (0.2 * base_salary)
    elif position == "content creator":
        base_salary = 35000
        salary = base_salary + (0.3 * base_salary)
    elif position == "digital marketing manager":
        base_salary = 70000
        salary = base_salary + (0.4 * base_salary)
    elif position == "social media manager":
        base_salary = 45000
        salary = base_salary + (0.4 * base_salary)
    else:
        raise ValueError("Invalid position")
    
    if edu_lvl == "high school":
        salary = base_salary + (0.05 * base_salary)
    elif edu_lvl == "associate degree":
        salary = base_salary + (0.1 * base_salary)
    elif edu_lvl == "bachelor degree":
        salary = base_salary + (0.2 * base_salary)
    elif edu_lvl == "master":
        salary = base_salary + (0.3 * base_salary)
    elif edu_lvl == "doctorate":
        salary = base_salary + (0.4 * base_salary)
    else:
        raise ValueError("Invalid education level")
    
    # Add experience year bonus if experience year is more than 5
    if int(exp_yr)> 5:
        salary += (0.05 * salary)

    return salary


@app.route("/AddEmp", methods=['GET','POST'])
def AddEmp():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        hire_date = request.form['hire_date']
        exp_yr = request.form['exp_yr'] #1-10
        edu_lvl = request.form['edu_lvl']
        # edu_lvl = request.form['edu_lvl'] #high school,associate's degree,bachelor's degree, master, doctorate
        position = request.form['position']
        # graphic designer, web developer, marketing analyst, content creator, digital marketing manager, social media manager
        # position = request.form.get['position']
        emp_image_file = request.files['emp_image_file']

        #calculate salary
        # salary = calculate_salary(exp_yr, edu_lvl, position)
         # Set base salaries for each position

        base_salaries = {'graphic designer': 30000, 'web developer': 50000, 'marketing analyst': 40000,
                        'content creator': 35000, 'digital marketing manager': 70000, 'social media manager': 45000}
        
        # Set education level multipliers
        edu_multipliers = {'high school': 0.9, 'associate degree': 1.0, 'bachelor degree': 1.1,
                        'master': 1.2, 'phd': 1.3}

        # base_salary = base_salaries[position]
        base_salary = base_salaries.get(position)
        if base_salary is None:
            raise ValueError("Invalid position")
        
        education_factor = edu_multipliers.get(edu_lvl, 1.0)
        
        # # Get bonus percentage based on position
        # bonus_dict = {'graphic designer': 0.05, 'web developer': 0.1, 'marketing analyst': 0.2,
        #                 'content creator': 0.3, 'digital marketing manager': 0.4, 'social media manager': 0.4}
        # bonus = bonus_dict.get(position, 0)
        

        salary = base_salary * education_factor
        # if position == "graphic designer":
        #     salary = base_salary + (0.05 * base_salary)
        # elif position == "web developer":
        #     salary = base_salary + (0.1 * base_salary)
        # elif position == "marketing analyst":
        #     salary = base_salary + (0.2 * base_salary)
        # elif position == "content creator":
        #     salary = base_salary + (0.3 * base_salary)
        # elif position == "digital marketing manager":
        #     salary = base_salary + (0.4 * base_salary)
        # elif position == "social media manager":
        #     salary = base_salary + (0.4 * base_salary)
        # else:
        #     raise ValueError("Invalid position")
        
        # if edu_lvl == "high school":
        #     salary = base_salary + (0.05 * base_salary)
        # elif edu_lvl == "associate degree":
        #     salary = base_salary + (0.1 * base_salary)
        # elif edu_lvl == "bachelor degree":
        #     salary = base_salary + (0.2 * base_salary)
        # elif edu_lvl == "master":
        #     salary = base_salary + (0.3 * base_salary)
        # elif edu_lvl == "doctorate":
        #     salary = base_salary + (0.4 * base_salary)
        # else:
        #     raise ValueError("Invalid education level")
        
        # Add experience year bonus if experience year is more than 5
        if int(exp_yr)> 5:
            salary += (0.05 * salary)

    # return salary

        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:

            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location,hire_date,exp_yr,edu_lvl,position,salary))
            db_conn.commit()
            emp_name = "" + first_name + " " + last_name
            # Uplaod image file in S3 #
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            s3 = boto3.resource('s3')

            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('AddEmpOutput.html', name=emp_name)
    else:
        return render_template('AddEmp.html')

@app.route("/ApplyLeaveEmp", methods=['GET','POST'])
def ApplyLeaveEmp():
    if request.method == 'POST':
        try:
            emp_id = request.form['emp_id']
            type_leave = request.form['type_leave']
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            insert_sql = "INSERT INTO emp_leave (emp_id, type_leave, start_date, end_date) VALUES (%s, %s, %s, %s)"
            cursor = db_conn.cursor()

            # execute the insert query with the values obtained from the HTML form
            cursor.execute(insert_sql, (emp_id, type_leave, start_date, end_date))

            # commit the changes to the database
            db_conn.commit()

            return render_template('ApplyLeaveEmp.html')

        except Exception as e:
            # handle the error and rollback changes
            db_conn.rollback()
            return "Error: " + str(e)
        finally:
            # close the database connection
            cursor.close()
    else:
        return render_template('ApplyLeaveEmp.html')

@app.route("/getInfo", methods=['GET'])
def GetEmployee():
    emp_id = request.form['emp_id']
    type_leave = request.form['type_leave']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    retrieve_sql = "SELECT FROM employee "

@app.route("/editInfo", methods = ['GET'])
def EditEmployee():
    return 

@app.route("/ReadEmp", methods=['GET', 'POST'])
def ReadEmployee():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
        cursor.execute(select_sql, (emp_id,))
        employee = cursor.fetchone()
        cursor.close()

        if employee:
            # Extract the employee information
            emp_info = {
                'first_name': employee[1],
                'last_name': employee[2],
                'pri_skill': employee[3],
                'location': employee[4],
                'hire_date': employee[5],
                'exp_year': employee[6],
                'edu_lvl': employee[7],
                'position': employee[8],
                'salary': employee[9]
            }

            # render the employee information in the EmployeeInfo.html template
            return render_template('EmployeeInfo.html', **emp_info)
        else:
            # if the employee ID is not found in the database
            error_msg = "Employee ID {} not found.".format(emp_id)
            return render_template('Error.html', error_msg=error_msg)
    else:
        return render_template('ReadEmp.html')
    

@app.route("/AllEmpInfo", methods=['GET','POST'])
def ReadAllEmployees():
    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM employee"
    cursor.execute(select_sql)
    employees = cursor.fetchall()
    cursor.close()

    if employees:
        # render the employee information in the EmployeeInfo.html template
        return render_template('AllEmpInfo.html', employees=employees)
    else:
        # if no employees found in the database
        error_msg = "No employees found."
        return render_template('Error.html', error_msg=error_msg)
    
@app.route("/UpdateEmp", methods=['GET','POST'])
def UpdateEmployee():
    emp_id = request.form['emp_id']

    # Retrieve the employee from the database
    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor.execute(select_sql, (emp_id,))
    employee = cursor.fetchone()

    if employee:
        # Update the specific employee information
        if 'first_name' in request.form:
            first_name = request.form['first_name']
            employee['first_name'] = first_name

        if 'last_name' in request.form:
            last_name = request.form['last_name']
            employee['last_name'] = last_name

        if 'pri_skill' in request.form:
            pri_skill = request.form['pri_skill']
            employee['pri_skill'] = pri_skill

        if 'location' in request.form:
            location = request.form['location']
            employee['location'] = location

        if 'hire_date' in request.form:
            hire_date = request.form['hire_date']
            employee['hire_date'] = hire_date

        if 'exp_year' in request.form:
            exp_year = request.form['exp_year']
            employee['exp_year'] = exp_year

        if 'edu_lvl' in request.form:
            edu_lvl = request.form['edu_lvl']
            employee['edu_lvl'] = edu_lvl

        if 'position' in request.form:
            position = request.form['position']
            employee['position'] = position

        if 'salary' in request.form:
            salary = request.form['salary']
            employee['salary'] = salary

        # Perform the update in the database
        update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, hire_date = %s, exp_year = %s, edu_lvl = %s, position = %s, salary = %s WHERE emp_id = %s"
        cursor.execute(update_sql, (employee['first_name'], employee['last_name'], employee['pri_skill'], employee['location'], employee['hire_date'],employee['exp_year'], employee['edu_lvl'], employee['position'], employee['salary'],emp_id))
        db_conn.commit()

        cursor.close()

        # Redirect the user to a success page or display a success message
        return render_template('UpdateSuccess.html')
    else:
        # Handle the case when employee is not found
        error_msg = "Employee ID {} not found.".format(emp_id)
        return render_template('Error.html', error_msg=error_msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

