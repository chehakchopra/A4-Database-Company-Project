# A4-Database-Company-Project

Assignment 4 Project Github Repo

## Setup

1) Clone our repository: `git clone https://github.com/chehakchopra/A4-Database-Company-Project.git`

2) Set up virtual environment then download required libraries (you must have python3 must be installed). If any of the modules fail to install, you can view `requirements.txt` and install them individually using `pip install <module name>`.

    __Mac:__

   `python3 -m venv .venv`

   `source .venv/bin/activate`

   `pip install flask`

   `pip install -r requirements.txt`

    __Windows:__

   `python3 -m venv .venv`

   `.venv\Scripts\activate`

   `pip install flask`

   `pip install -r requirements.txt`

3) Set up a database, assuming postgresql is installed (replace 'postgres' with your username if you aren't using the default username). Create a database named `company_db` in Postgres, then populate the database using one of the following:
   * Command line:
     * `createdb -U postgres company_db`
     * `psql -U postgres -d company_db -a -f company_v3.02.sql`
     * `psql -U postgres -d company_db -a -f team_setup.sql`
   * psql (shell/interactive environment within command line):
     * `psql -U postgres` in the command line
     * `create database company_db;`
     * Switch to the  `company_db` database: `\c company_db`
     * `\i company_v3.02.sql`
     * `\i team_setup.sql`
   * pgAdmin4:
     * From the menu, go to `Object > Create > Database...`
     * Input the database name: `company_db`
     * Click `Save`
     * Right click `company_db` and go to its Query Tool
     * Open the `company_v3.02.sql` from the file explorer, then click execute
     * Open the `team_setup.sql` from the file explorer, then click execute

4) Run the project in flask: `flask run`

5) Input the username, password, and port for the database when prompted in the command line.

6) Open the outputted link in a browser! ([Likely 127.0.0.1:5000](http://127.0.0.1:5000/))

## About Indexes

All primary keys already have indexes in postgresql, so we chose indexes for other fields

```postgresql
CREATE INDEX idx_workson_pno ON Works_On (Pno);
CREATE INDEX idx_workson_essn ON Works_On (Essn);
CREATE INDEX idx_dept_dname ON Department (Dname);
```

Our indexes:

* Should improve the performance of retrieving data from their respective tables
* are Our overall most commonly used fields in JOIN or WHERE conditions
* All speed up the retrieval time of:
  * The Employee data for the Home/Employee page (A2) and CSV (Bonus).
  * The Project data on Projects (A3)
* `idx_workson_pno` & `idx_workson_essn` speed up the retrieval time of the Employee data on the Project page (A4)
* `idx_workson_essn` & `idx_dept_dname` speed up the retrieval time of Department data on the Managers page (A6)
* In addition to aforementioned uses, `idx_dept_name` also improves the retrieval time of Department data (names) for dropdowns present on the Add/Edit Employee pages (A5)
