
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Connect to database
def get_db_connection():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create employee table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Dashboard
@app.route("/")
def home():

    conn = get_db_connection()

    employees = conn.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    ).fetchall()

    total_employees = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    total_departments = conn.execute(
        "SELECT COUNT(DISTINCT department) FROM employees"
    ).fetchone()[0]

    average_salary = conn.execute(
        "SELECT AVG(salary) FROM employees"
    ).fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        employees=employees,
        total_employees=total_employees,
        total_departments=total_departments,
        average_salary=round(average_salary, 2)
    )


# Add employee
@app.route("/add", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"]
        salary = float(request.form["salary"])

        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO employees
                (name, email, department, salary)
                VALUES (?, ?, ?, ?)
            """, (name, email, department, salary))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "An employee with this email already exists!"

        conn.close()

        return redirect("/")

    return render_template("add_employee.html")


# Edit employee
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    conn = get_db_connection()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (id,)
    ).fetchone()

    if employee is None:
        conn.close()
        return "Employee not found", 404

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"]
        salary = float(request.form["salary"])

        try:
            conn.execute("""
                UPDATE employees
                SET name = ?, email = ?, department = ?, salary = ?
                WHERE id = ?
            """, (name, email, department, salary, id))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "This email address is already registered!", 400

        conn.close()
        return redirect("/")

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )

if __name__ == "__main__":
    create_table()
    app.run(debug=True)

