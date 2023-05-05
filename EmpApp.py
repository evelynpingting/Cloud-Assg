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
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

def calculate_salary(exp_yr, edu_lvl, position):
    # Set base salaries for each position
    base_salaries = {'graphic designer': 30000, 'web developer': 50000, 'marketing analyst': 40000,
                     'content creator': 35000, 'digital marketing manager': 70000, 'social media manager': 45000}
    
    base_salary = base_salaries[position]
    if edu_lvl == "high school":
        salary = base_salary + (0.05 * base_salary)
    elif edu_lvl == "associate's degree":
        salary = base_salary + (0.1 * base_salary)
    elif edu_lvl == "bachelor's degree":
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

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    hire_date = request.form['hire_date']
    exp_yr = request.form['exp_yr'] #1-10
    edu_lvl = request.form['edu_lvl'] #high school,associate's degree,bachelor's degree, master, doctorate
    position = request.form['position'] # graphic designer, web developer, marketing analyst, content creator, digital marketing manager, social media manager

    emp_image_file = request.files['emp_image_file']

    #calculate salary
    salary = calculate_salary(exp_yr, edu_lvl, position)

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

@app.route("/applyleave", methods=['GET', 'POST'])
def ApplyLeave():
    emp_id = request.form['emp_id']
    type_leave = request.form['type_leave']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    insert_sql = "INSERT INTO emp_leave VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()



    return render_template('AddEmp.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

