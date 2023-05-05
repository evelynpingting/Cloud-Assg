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

        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:

            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location,hire_date,exp_yr,edu_lvl,position))
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

@app.route("/ReadEmp", methods=['GET','POST'])
def ReadEmployee():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
        cursor.execute(select_sql, (emp_id,))
        employee = cursor.fetchone()
        cursor.close()

        if employee:
            # render the employee information in a new HTML page
            return render_template('EmployeeInfo.html', employee=employee)
        else:
            # if the employee ID is not found in the database
            error_msg = "Employee ID {} not found.".format(emp_id)
            return render_template('Error.html', error_msg=error_msg)
    else:
        return render_template('ReadEmp.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

