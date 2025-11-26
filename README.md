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

3) Set up a database (TODO: figure out a better way to do this step later)

   * Create a database named `company_db` in Postgres using either the command line or pgadmin
   * Link the created database to our code by changing values in the `get_db_connection` function in `app.py` as necessary (user, password)
     * Idea: allow user to enter username/password of their pgadmin on command line? So that the run command is `flask run user pwd` (probably poor practice though, may be better as a prompt type of think like ssh/telnet do)
   * Run the following commands to populate the database (replace 'postgres' with your username if you aren't using the default username)

    `psql -U postgres -d company_db -a -f company_v3.02.sql`

    `psql -U postgres -d company_db -a -f team_setup.sql`

4) Run the project in flask: `flask run`

5) Open the outputted link in a browser! ([Likely 127.0.0.1:5000](http://127.0.0.1:5000/))

## About Indexes

* An index for any of the following may be useful, as they're repeated:
  * get employee (due to csv & view)
    * manager
  * get department (bc filters on mutiple pages)
