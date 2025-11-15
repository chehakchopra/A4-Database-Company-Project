from flask import Flask, render_template, request, redirect, url_for, session, flash  # noqa E501
import psycopg2
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    # DB Connection
    conn = psycopg2.connect(
        host="localhost",
        dbname="company_db",       
        user="postgres",            
        password="12345",   
        port="5432"
    )
    return conn


def login_required(f):
    # Login Reqd
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["GET", "POST"])
# Login
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM app_user WHERE username = %s",
            (username,))
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
    # Homepage
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM employee;")
    total_employees = cur.fetchone()[0]
    cur.close()
    conn.close()

    return render_template("home.html",
                           username=session["username"],
                           total_employees=total_employees)


@app.route("/employees", methods=["GET"])
@login_required
def employees():
    # Employee Overview
    conn = get_db_connection()
    cur = conn.cursor()

    # Get filters
    search_name = request.args.get("search_name", "").strip()
    selected_dept = request.args.get("department", "")

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
        ORDER BY e.fname;
    """

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
        search_name=search_name
    )


@app.route("/projects", methods=["GET"])
@login_required
def projects():
    # Project Overview
    conn = get_db_connection()
    cur = conn.cursor()

    search_name = request.args.get("search_name", "").strip()
    selected_dept = request.args.get("department", "")

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

    query += """
        GROUP BY p.pnumber, p.pname, d.dname
        ORDER BY p.pnumber;
    """

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
        selected_dept=selected_dept
    )


@app.route("/logout")
def logout():
    # Logout
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Run app.py
    app.run(debug=True)
