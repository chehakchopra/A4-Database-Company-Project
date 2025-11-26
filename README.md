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

* An index for any of the following may be useful, as they're repeated:
  * get employee (due to csv & view)
    * manager
  * get department (bc filters on mutiple pages)
