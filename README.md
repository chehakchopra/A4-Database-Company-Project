# A4-Database-Company-Project
Assignment 4 Project Github Repo

## Setup

1) Clone our repository: `git clone https://github.com/chehakchopra/A4-Database-Company-Project.git`

2) Set up virtual environment then download required libraries (you must have python3 must be installed)

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

4) Set up a database (todo: figure out a better way to do this step later)
* Create a database named `company_db` in Postgres using either the command line or pgadmin
* Link the created database to our code by changing values in the get_db_connection function of `app.py` as necessary (user, password)
* Run the following commands to populate the database (replace 'postgres' with your username if you aren't using the default username)

`psql -U postgres -d company_db -a -f company_v3.02.sql`

`psql -U postgres -d company_db -a -f team_setup.sql`

4) Run the project in flask: `flask run`

6) Open the outputted link in a browser! 


