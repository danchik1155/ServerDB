from flask import Flask, render_template, request
import time
import psycopg2

app = Flask(__name__)

@app.route("/cabinet", methods=['POST', 'GET'])
def cabinet():
    if request.method == 'POST':
        return render_template('cabinet.html', fio='Jerry')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/sale.html")
def sale():
    return render_template('sale.html')

@app.route("/registration.html")
def registration():
    return render_template('registration.html')



# @app.route("/stylelog_reg.css")
# def stylelog_reg():
#     return render_template('stylelog_reg.css')
#
# @app.route("/stylemod.css")
# def stylemod():
#     return render_template('stylemod.css')

@app.route("/status")
def status():
    return {'status':'true', 'name':'TG', 'time': time.asctime()}

# with psycopg2.connect(dbname='database', user='db_user',password='mypassword', host='localhost') as conn:
#
#     # Open a cursor to perform database operations
#     with conn.cursor() as cur:
#
#         # Execute a command: this creates a new table
#         cur.execute("""
#             CREATE TABLE test (
#                 id serial PRIMARY KEY,
#                 num integer,
#                 data text)
#             """)
#
#         # Pass data to fill a query placeholders and let Psycopg perform
#         # the correct conversion (no SQL injections!)
#         cur.execute(
#             "INSERT INTO test (num, data) VALUES (%s, %s)",
#             (100, "abc'def"))
#
#         # Query the database and obtain data as Python objects.
#         cur.execute("SELECT * FROM test")
#         cur.fetchone()
#         # will return (1, 100, "abc'def")
#
#         # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
#         # of several records, or even iterate on the cursor
#         for record in cur:
#             print(record)
#
#         # Make the changes to the database persistent
#         conn.commit()

app.run()

