from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime
import uuid

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

# def ping(self, reconnect=True):
#     """
#     Check if the server is alive.

#     :param reconnect: If the connection is closed, reconnect.
#     :raise Error: If the connection is closed and reconnect=False.
#     """
#     if self._sock is None:
#         if reconnect:
#             self.connect()
#             reconnect = False
#         else:
#             raise err.Error("Already closed")
#     try:
#         self._execute_command(COMMAND.COM_PING, "")
#         self._read_ok_packet()
#     except Exception:
#         if reconnect:
#             self.connect()
#             self.ping(False)
#         else:
#             raise

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('MainMenu.html')


@app.route("/AboutUsYk")
def aboutYk():
    return render_template('AboutUsYk.html')

@app.route("/AboutUsPt")
def aboutPt():
    return render_template('AboutUsPt.html')

@app.route("/AboutUsSy")
def aboutSy():
    return render_template('AboutUsSy.html')


@app.route("/Error")
def Error():
    return render_template('Error.html')

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
        edu_lvl = request.form['edu_lvl'] #high school,associate degree,bachelor degree, master, phd
        position = request.form['position'] # graphic designer, web developer, marketing analyst, content creator, digital marketing manager, social media manager
        emp_image_file = request.files['emp_image_file']

        #calculate salary
        base_salaries = {'graphic designer': 3000, 'web developer': 5000, 'marketing analyst': 4000,
                        'content creator': 3500, 'digital marketing manager': 7000, 'social media manager': 4500}
        
        # Set education level multipliers
        edu_multipliers = {'high school': 0.9, 'associate degree': 1.0, 'bachelor degree': 1.1,
                        'master': 1.2, 'phd': 1.3}

        base_salary = base_salaries.get(position)
        if base_salary is None:
            raise ValueError("Invalid position")
        
        education_factor = edu_multipliers.get(edu_lvl, 1.0)

        salary = base_salary * education_factor

        if int(exp_yr)> 5:
            salary += (0.05 * salary)

    
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
        return render_template('AddEmpOutput.html', id=emp_id,name=emp_name, position=position,salary=salary,exp_yr=exp_yr)
    else:
        return render_template('AddEmp.html')


@app.route("/ApplyLeaveEmp", methods=['GET','POST'])
def ApplyLeaveEmp():
    if request.method == 'POST':
        try:
            emp_id = request.form['emp_id']
            
            # Check if the employee ID exists in the database
            cursor = db_conn.cursor()
            select_sql = "SELECT * FROM employee WHERE emp_id = %s"
            cursor.execute(select_sql, (emp_id,))
            employee = cursor.fetchone()
            
            if employee:
                type_leave = request.form['type_leave']
                start_date = request.form['start_date']
                end_date = request.form['end_date']

                insert_sql = "INSERT INTO emp_leave (emp_id, type_leave, start_date, end_date) VALUES (%s, %s, %s, %s)"
                     
                # execute the insert query with the values obtained from the HTML form
                cursor.execute(insert_sql, (emp_id,type_leave, start_date, end_date))

                # commit the changes to the database
                db_conn.commit()

                return render_template('ApplyLeaveSuccess.html',emp_id=emp_id,type_leave=type_leave,start_date=start_date,end_date=end_date)
            else:
                # Handle the case when employee is not found
                error_msg = "Employee ID {} not found.".format(emp_id)
                return render_template('Error.html', error_msg=error_msg)

        except Exception as e:
            # handle the error and rollback changes
            db_conn.rollback()
            return "Error: " + str(e)
        finally:
            # close the database connection
            cursor.close()
    else:
        return render_template('ApplyLeaveEmp.html')

@app.route("/ApplyLeaveSuccess")
def ApplyLeaveSuccess():
    return render_template('ApplyLeaveSuccess.html')
    
    

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
def CheckEmployee():
    if request.method == 'POST':
        emp_id = request.form['emp_id']

        # Check if the employee ID exists in the database
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
        cursor.execute(select_sql, (emp_id,))
        employee = cursor.fetchone()
        #cursor.close()

        if employee:
            # Convert the tuple to a dictionary
            employee_dict = {
                'emp_id': employee[0],
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

            # Update the specific employee information
            if 'first_name' in request.form:
                employee_dict['first_name'] = request.form['first_name']

            if 'last_name' in request.form:
                employee_dict['last_name'] = request.form['last_name']

            if 'pri_skill' in request.form:
                employee_dict['pri_skill'] = request.form['pri_skill']

            if 'location' in request.form:
                employee_dict['location'] = request.form['location']

            if 'hire_date' in request.form:
                employee_dict['hire_date'] = request.form['hire_date']

            if 'exp_year' in request.form:
                employee_dict['exp_year'] = request.form['exp_year']

            if 'edu_lvl' in request.form:
                employee_dict['edu_lvl'] = request.form['edu_lvl']

            if 'position' in request.form:
                employee_dict['position'] = request.form['position']

            if 'salary' in request.form:
                employee_dict['salary'] = request.form['salary']

            # Perform the update in the database
            update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, hire_date = %s, exp_year = %s, edu_lvl = %s, position = %s, salary = %s WHERE emp_id = %s"
                
            cursor.execute(update_sql, (
                employee_dict['first_name'],
                employee_dict['last_name'],
                employee_dict['pri_skill'],
                employee_dict['location'],
                employee_dict['hire_date'],
                employee_dict['exp_year'],
                employee_dict['edu_lvl'],
                employee_dict['position'],
                employee_dict['salary'],
                emp_id
            ))
            db_conn.commit()

            cursor.close()

            # Redirect the user to a success page or display a success message
            return render_template('UpdateSuccess.html')
        else:
            # Handle the case when employee is not found
            error_msg = "Employee ID {} not found.".format(emp_id)
            return render_template('Error.html', error_msg=error_msg)
    else:
        return render_template('UpdateEmp.html')
    

@app.route("/UpdateSuccess", methods=['GET','POST'])
def UpdateSuccess():
    if request.method == 'POST':
        return render_template('UpdateSucess.html')
    else:
        return render_template('UpdateSuccess.html')

@app.route("/DeleteEmp", methods=['GET','POST'])
def DeleteEmployee():
    if request.method == 'POST':
        emp_id = request.form['emp_id']

        # Check if the employee ID exists in the database
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
        cursor.execute(select_sql, (emp_id,))
        employee = cursor.fetchone()

        if employee:
            # Execute the DELETE statement to remove the employee record
            delete_sql = "DELETE FROM employee WHERE emp_id = %s"  
            cursor.execute(delete_sql, (emp_id,))
            db_conn.commit()
            cursor.close()

            success_msg = "Employee ID {} deleted successfully.".format(emp_id)
            return render_template('DeleteEmp.html', success_msg=success_msg)
        else:
            error_msg = "Employee ID {} not found.".format(emp_id)
            return render_template('Error.html', error_msg=error_msg)
    else:
        return render_template('DeleteEmp.html')

    
from datetime import datetime

@app.route("/AddAttendance", methods=['GET','POST'])
def AddAttendance():
    if request.method == "POST":
        date = datetime.now().strftime("%Y-%m-%d")
        emp_id = request.form['emp_id']
        time = datetime.now().strftime("%H:%M:%S")

        # Check if the employee ID exists in the database
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
         
        cursor.execute(select_sql, (emp_id,))
        employee = cursor.fetchone()

        if employee:
            insert_sql = "INSERT INTO employeeAttendance (date, emp_id, time) VALUES (%s, %s, %s)"
            cursor.execute(insert_sql, (date, emp_id, time))
            db_conn.commit()
            cursor.close()
            success_msg = "Attendance added successfully for employee ID {}.".format(emp_id)
            return render_template('AddAttendance.html', success_msg=success_msg)
        
        else:
            error_msg = "Employee ID {} not found.".format(emp_id)
            return render_template('Error.html', error_msg=error_msg)
    
    else:
        return render_template('AddAttendance.html')
 

    
@app.route("/CheckAttendanceRecord", methods=['GET','POST'])
def CheckAttendanceRecord():
    if request.method == "POST":
        # get the date from the query parameter
        date =  request.form['date']
        date = datetime.strptime(date, "%Y-%m-%d").date()

        # retrieve the attendance record from the database
        cursor = db_conn.cursor()
        select_sql = "SELECT employeeAttendance.date, employeeAttendance.emp_id, employee.first_name, employee.last_name, employeeAttendance.time FROM employeeAttendance INNER JOIN employee ON employeeAttendance.emp_id=employee.emp_id WHERE date=%s"
            
        cursor.execute(select_sql, (date,))
        attendance_info = cursor.fetchall()
        cursor.close()
        if attendance_info:
            # render the attendance record in the AttendanceInfo.html template
            return render_template('AttendanceInfo.html', attendance_info=attendance_info)
        else:
            # if no attendance record found in the database
            error_msg = "No employees found."
            return render_template('Error.html', error_msg=error_msg)
    else:
        return render_template('CheckAttendanceRecord.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

