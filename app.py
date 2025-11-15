from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"


#DB Connection
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
            return redirect(url_for("home"))
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
            e.fname || ' ' || e.lname AS full_name,
            d.dname AS department,
            COUNT(DISTINCT dep.dependent_name) AS total_dependents,
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
        params.extend([f"%{search_name.lower()}%", f"%{search_name.lower()}%"])

    if selected_dept:
        conditions.append("d.dname = %s")
        params.append(selected_dept)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY e.ssn, e.fname, e.lname, d.dname
    """

    # Sorting
    if sort_by:
        query += " ORDER BY "
        if sort_by == "hours":
            query += "total_hours "
        else:
            query += "full_name "

        query += "DESC " if sort_dir == "desc" else "ASC "
    else:
        query += " ORDER BY full_name ASC "

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

    if sort_by == "hours":
        query += " ORDER BY total_hours "
    else:
        query += " ORDER BY total_employees "

    query += "DESC " if sort_dir == "desc" else "ASC "

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


@app.route("/employee/add", methods=["GET", "POST"])
@login_required
def add_employee():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT dnumber, dname FROM department ORDER BY dname;")
    departments = cur.fetchall()

    cur.execute("SELECT ssn, fname || ' ' || lname FROM employee ORDER BY fname;")
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

    cur.execute("SELECT ssn, fname || ' ' || lname FROM employee WHERE ssn <> %s;", (ssn,))
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

    cur.execute("SELECT 1 FROM dependent WHERE essn = %s LIMIT 1;", (ssn,))
    dep = cur.fetchone()

    cur.execute("SELECT 1 FROM works_on WHERE essn = %s LIMIT 1;", (ssn,))
    work = cur.fetchone()

    cur.execute("SELECT 1 FROM department WHERE mgr_ssn = %s LIMIT 1;", (ssn,))
    mgr = cur.fetchone()

    if dep or work or mgr:
        flash("Cannot delete employee due to dependencies.", "danger")
        return redirect(url_for("employees"))

    try:
        cur.execute("DELETE FROM employee WHERE ssn = %s;", (ssn,))
        conn.commit()
        flash("Employee deleted.", "info")
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
