# import time
import psycopg2
from flask import Flask, render_template, request
from flask_migrate import Migrate

from models import db, InfoModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/cursach"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return form()

@app.route('/form')
def form():
    return render_template("form.html")

@app.route('/users')
def users():
    with psycopg2.connect(dbname='cursach', user='postgres', password='password', host='localhost') as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            s = []
            wiwod = '''<table id="table" border="1" width="100%" cellpadding="5">\n'''
            wiwod = wiwod + ' <tr>'
            cur.execute("SELECT * FROM info_table")
            for i in cur.fetchall():
                s.append(i)
            cur.execute('''select column_name from information_schema.columns 
            where information_schema.columns.table_name='info_table';''')
            for i in cur.fetchall():
                for j in i:
                    wiwod = wiwod + '<th> ' + str(j) + ' </th>'
            wiwod = wiwod + '</tr>\n'
            for i in s:
                wiwod = wiwod + ' <tr>'
                for j in i:
                    wiwod = wiwod + '<th> ' + str(j) + ' </th>'
                wiwod = wiwod + '</tr>\n'
            wiwod = wiwod + "</table>"
            conn.commit()
            return wiwod


@app.route('/login', methods=['POST', 'GET'])

def login():
    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        new_user = InfoModel(name=name, age=age)
        db.session.add(new_user)
        db.session.commit()
        return f"Done!!"


if __name__ == '__main__':
    app.run(debug=True)