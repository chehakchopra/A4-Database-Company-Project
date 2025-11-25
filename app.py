from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import check_password_hash
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        dbname="company_db",
        user="postgres",
        password="12345",
        port="5432"
    )
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def whitelist(input):
    # Source - https://stackoverflow.com/questions/56159087/how-can-i-whitelist-characters-from-a-string-in-python-3
    # Posted by Ajax1234
    # Retrieved 2025-11-25, License - CC BY-SA 4.0
    # Used as reference
    return re.sub('[^a-zA-Z0-9_ ]', '', input)


def is_valid(input):
    # Source - https://stackoverflow.com/questions/5698267/efficient-way-to-search-for-invalid-characters-in-python
    # Posted by ridgerunner, modified by community. See post 'Timeline' for change history
    # Retrieved 2025-11-25, License - CC BY-SA 3.0
    # Used as reference
    if re.search('[^a-zA-Z0-9_ ]', input):
        return False
    else:
        return True


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM app_user WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("employees"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/home")
@login_required
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM employee;")
    total_employees = cur.fetchone()[0]
    cur.close()
    conn.close()

    return render_template(
        "home.html",
        username=session["username"],
        total_employees=total_employees
    )


@app.route("/employees", methods=["GET"])
@login_required
def employees():

    conn = get_db_connection()
    cur = conn.cursor()

    search_name = request.args.get("search_name", "").strip()
    selected_dept = request.args.get("department", "")
    sort_by = request.args.get("sort_by", "")
    sort_dir = request.args.get("sort_dir", "asc")

    query = """
        SELECT
            e.ssn,
            e.fname || ' ' || e.minit || '. ' || e.lname AS full_name,
            d.dname AS department,
            COUNT(DISTINCT dep.dependent_name) AS total_dependents,
            COUNT(DISTINCT p.pname) AS num_projects,
            STRING_AGG(DISTINCT p.pname, ', ') AS projects,
            COALESCE(SUM(w.hours), 0) AS total_hours
        FROM employee e
        LEFT JOIN department d ON e.dno = d.dnumber
        LEFT JOIN works_on w ON e.ssn = w.essn
        LEFT JOIN project p ON w.pno = p.pnumber
        LEFT JOIN dependent dep ON e.ssn = dep.essn
    """

    conditions = []
    params = []

    if search_name:
        conditions.append("(LOWER(e.fname) LIKE %s OR LOWER(e.lname) LIKE %s)")
        wl_search_name = whitelist(search_name)
        params.extend([f"%{wl_search_name.lower()}%",
                       f"%{wl_search_name.lower()}%"])

    if selected_dept:
        conditions.append("d.dname = %s")
        params.append(whitelist(selected_dept))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY e.ssn, e.fname, e.lname, d.dname
    """

    # Sorting (by default, no sorting)
    # ensure the valid sorting options are selected
    if sort_by and sort_dir:
        sort_condition = " ORDER BY "
        sort_condition += "total_hours" if whitelist(sort_by) == "hours" else "e.fname"
        sort_condition += " DESC" if whitelist(sort_dir) == "desc" else " ASC"
        query += sort_condition
    query += ";"

    cur.execute(query, params)
    employees = cur.fetchall()

    cur.execute("SELECT DISTINCT dname FROM department ORDER BY dname;")
    departments = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "employees.html",
        employees=employees,
        departments=departments,
        selected_dept=selected_dept,
        search_name=search_name,
        sort_by=sort_by,
        sort_dir=sort_dir
    )


@app.route("/projects", methods=["GET"])
@login_required
def projects():

    conn = get_db_connection()
    cur = conn.cursor()

    search_name = request.args.get("search_name", "").strip()
    selected_dept = request.args.get("department", "")
    sort_by = request.args.get("sort_by", "")
    sort_dir = request.args.get("sort_dir", "asc")

    query = """
        SELECT
            p.pnumber,
            p.pname,
            d.dname AS department,
            COUNT(DISTINCT w.essn) AS total_employees,
            COALESCE(SUM(w.hours), 0) AS total_hours
        FROM project p
        LEFT JOIN department d ON p.dnum = d.dnumber
        LEFT JOIN works_on w ON p.pnumber = w.pno
    """

    conditions = []
    params = []

    if search_name:
        conditions.append("LOWER(p.pname) LIKE %s")
        params.append(f"%{search_name.lower()}%")

    if selected_dept:
        conditions.append("d.dname = %s")
        params.append(selected_dept)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY p.pnumber, p.pname, d.dname "

    # Sorting (by default, no sorting)
    # ensure the valid sorting options are selected
    if sort_by and sort_dir:
        sort_condition = " ORDER BY "
        sort_condition += "total_hours" if whitelist(sort_by) == "hours" else "total_employees"
        sort_condition += " DESC" if whitelist(sort_dir) == "desc" else " ASC"
        query += sort_condition
    query += ";"

    cur.execute(query, params)
    projects = cur.fetchall()

    cur.execute("SELECT DISTINCT dname FROM department ORDER BY dname;")
    departments = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "projects.html",
        projects=projects,
        departments=departments,
        search_name=search_name,
        selected_dept=selected_dept,
        sort_by=sort_by,
        sort_dir=sort_dir
    )


@app.route("/projects/<pid>", methods=["GET", "POST"])
@login_required
def project(pid):

    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "POST":
        try:
            emp_id = request.form["emp_id"]
            hours = request.form["hours"]
            cur.execute(
                "INSERT INTO Works_On VALUES (%s, %s, %s) ON CONFLICT (Essn, Pno) DO UPDATE SET Hours = Works_On.Hours + EXCLUDED.Hours;", (emp_id, pid, hours))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(
                f"Error: Ensure you selected an employee and hours are between 0-999", "danger")

    # Query to retrieve all employees on this project with Full Name and Hours
    cur.execute("SELECT Fname, Minit, Lname, Hours FROM Works_on INNER JOIN Employee ON Employee.Ssn = Works_on.Essn WHERE Pno = %s", (pid,))
    emps_on_project = cur.fetchall()
    
    cur.execute("SELECT Ssn, Fname, Minit, Lname FROM Employee ORDER BY Fname")
    employees = cur.fetchall()
    
    cur.execute("SELECT Pname FROM Project WHERE Pnumber = %s", (pid,))
    proj_name = cur.fetchone()
    
    print(proj_name)

    cur.close()
    conn.close()
    return render_template(
        "project.html", proj_name=proj_name, emps_on_project=emps_on_project, employees=employees
    )


@app.route("/managers")
@login_required
def managers():

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT
            d.dname,
            d.dnumber,
            COALESCE(e.fname || ' ' || e.minit || '. ' || e.lname, 'None') AS manager_name,
            COUNT(DISTINCT emp.ssn) AS employee_count,
            COALESCE(SUM(w.hours), 0) AS total_hours
        FROM department d
        LEFT JOIN employee e ON d.mgr_ssn = e.ssn
        LEFT JOIN employee emp ON emp.dno = d.dnumber
        LEFT JOIN works_on w ON w.essn = emp.ssn
        GROUP BY d.dname, d.dnumber, manager_name
        ORDER BY d.dnumber;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("managers.html", managers=rows)


@app.route("/employee/add", methods=["GET", "POST"])
@login_required
def add_employee():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT dnumber, dname FROM department ORDER BY dname;")
    departments = cur.fetchall()

    cur.execute(
        "SELECT ssn, fname || ' ' || lname FROM employee ORDER BY fname;")
    supervisors = cur.fetchall()

    if request.method == "POST":
        fname = request.form["fname"]
        minit = request.form["minit"]
        lname = request.form["lname"]
        ssn = request.form["ssn"]
        address = request.form["address"]
        sex = request.form["sex"]
        salary = request.form["salary"]
        super_ssn = request.form["super_ssn"] or None
        dno = request.form["dno"]
        bdate = request.form["bdate"]
        empdate = request.form["empdate"]

        try:
            cur.execute("""
                INSERT INTO employee
                (fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, bdate, empdate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, bdate, empdate))

            conn.commit()
            flash("Employee added successfully!", "success")
            return redirect(url_for("employees"))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash(
                "Error: An employee with the provided SSN already exists",
                "danger")
        except Exception as e:
            conn.rollback()
            flash(f"Error adding employee: {e}", "danger")

    cur.close()
    conn.close()

    return render_template("add_employee.html",
                           departments=departments,
                           supervisors=supervisors)


@app.route("/employee/<ssn>/edit", methods=["GET", "POST"])
@login_required
def edit_employee(ssn):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employee WHERE ssn = %s;", (ssn,))
    emp = cur.fetchone()

    if not emp:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees"))

    cur.execute("SELECT dnumber, dname FROM department ORDER BY dname;")
    departments = cur.fetchall()

    cur.execute(
        "SELECT ssn, fname || ' ' || minit || '. ' || lname FROM employee WHERE ssn <> %s;",
        (ssn,))
    supervisors = cur.fetchall()

    if request.method == "POST":
        address = request.form["address"]
        salary = request.form["salary"]
        dno = request.form["dno"]
        super_ssn = request.form["super_ssn"] or None

        try:
            cur.execute("""
                UPDATE employee
                SET address = %s, salary = %s, dno = %s, super_ssn = %s
                WHERE ssn = %s;
            """, (address, salary, dno, super_ssn, ssn))

            conn.commit()
            flash("Employee updated successfully!", "success")
            return redirect(url_for("employees"))

        except Exception as e:
            conn.rollback()
            flash(f"Error updating employee: {e}", "danger")

    cur.close()
    conn.close()

    return render_template("edit_employee.html",
                           emp=emp,
                           departments=departments,
                           supervisors=supervisors)


@app.route("/employee/<ssn>/delete")
@login_required
def delete_employee(ssn):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM department WHERE mgr_ssn = %s LIMIT 1;", (ssn,))
    dept_mgr = cur.fetchone()

    if dept_mgr:
        flash("Cannot delete employee: They are a department manager.",
              "danger")
        return redirect(url_for("employees"))

    cur.execute("SELECT 1 FROM employee WHERE super_ssn = %s LIMIT 1;",
                (ssn,))
    emp_mgr = cur.fetchone()

    if emp_mgr:
        flash("Cannot delete employee: They are a supervisor.", "danger")
        return redirect(url_for("employees"))

    try:
        cur.execute("DELETE FROM employee WHERE ssn = %s;", (ssn,))
        conn.commit()
        flash("Employee deleted.", "info")
    except psycopg2.DatabaseError as e:
        conn.rollback()
        detail = e.pgerror
        if "works_on" in e.pgerror:
            detail = "Employee is assigned to a project"
        if "dependent" in e.pgerror:
            detail = "Employee has dependents"
        flash(f"Could not delete employee: {detail}.", "danger")
    except Exception as e:
        conn.rollback()
        flash("Error deleting employee: " + str(e), "danger")

    return redirect(url_for("employees"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
