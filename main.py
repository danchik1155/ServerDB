# import time
#
#
# class Messenger:
#     db = []
#     requested_count = 0
#
#     def send_message(self, name, text):
#         timestamp = time.asctime()
#         self.db.append({
#             'name': name,
#             'text': text,
#             'timestamp': timestamp
#         })
#
#     def get_messages(self):
#         return self.db
#
#     def get_new_messages(self):
#         new_messages = self.db[self.requested_count:]
#         self.requested_count += len(new_messages)
#         return new_messages
#
#
# messenger = Messenger()
# messenger.send_message('Jack', 'abc')
# messenger.send_message('Jack', 'abcd')
# print('All:', messenger.get_messages())
# print('New:', messenger.get_new_messages())
# print()
#
# messenger.send_message('Black', 'Hello!')
# print('All:', messenger.get_messages())
# print('New:', messenger.get_new_messages())
# print()
#
# messenger.send_message('Black', 'Hello2')
# print('All:', messenger.get_messages())
# print('New:', messenger.get_new_messages())
# print()
#
# messenger.send_message('Black', 'Hello3')
# print('All:', messenger.get_messages())
# print('New:', messenger.get_new_messages())

from flask import Flask, render_template, request
from flask_migrate import Migrate
from models import db, InfoModel
import psycopg2
# from sqlalchemy import create_engine

# engine = create_engine('postgresql+psycopg2://@localhost/flask')

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
            return wiwod
            conn.commit()

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