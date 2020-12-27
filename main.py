import time
import psycopg2

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate

from models import db, InfoModel, Clients, Contactdetailsclients, Secretdate, Card

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/cursach"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'so so very very secret'
db.init_app(app)
manager = LoginManager(app)
migrate = Migrate(app, db)


def getinffromtable(table_name):
    with psycopg2.connect(dbname='cursach', user='postgres', password='password', host='localhost') as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            s = []
            wiwod = '''<table id="table" border="1" width="100%" cellpadding="5">\n'''
            wiwod = wiwod + ' <tr>'
            cur.execute(f"SELECT * FROM {table_name}")
            for i in cur.fetchall():
                s.append(i)
            cur.execute(f'''select column_name from information_schema.columns 
               where information_schema.columns.table_name='{table_name}';''')
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


@app.route('/')
def index():
    return redirect('/login')


@app.route('/form')
def form():
    return render_template("form.html")


@app.route('/users')
def users():
    return getinffromtable('clients')


@app.route("/cabinet", methods=['POST', 'GET'])
@login_required
def cabinet():
    if request.method == 'GET':
        user = db.session.query(Clients, Contactdetailsclients, Card).filter_by(email=current_user.email).first()
        return render_template('cabinet.html', fio=current_user.fio, role=current_user.id_role, amount=user.Card.amount,
                               book=(getinffromtable('books')))


@app.route("/login", methods=['POST', 'GET'])
def login_pg():
    if current_user.is_authenticated:
        return redirect('/cabinet')

    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = db.session.query(Clients, Contactdetailsclients, Secretdate).filter_by(email=login).first()
        print(user)

        if user and check_password_hash(user.Secretdate.hash_password, password):
            login_user(user.Clients)
            next_page = request.args.get('next')
            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect('/cabinet')
        else:
            flash('Login or password is not correct')

    return render_template('login.html')
    # if request.method == 'GET':
    #     return render_template('login.html')
    #
    # if request.method == 'POST':
    #     name = request.form['name']
    #     age = request.form['age']
    #     new_user = InfoModel(name=name, age=age)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return f"Done!!"


# def login():
#     return render_template('login.html')

@app.route("/book")
def book():
    return render_template('book.html')


@app.route("/sale")
@login_required
def sale():
    return render_template('sale.html')


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')

    if request.method == 'POST':
        fio = request.form['fio']
        created = time.asctime()  # использовать дату
        dob = request.form['dob']  # определить формат
        role = 0
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        hash_password = generate_password_hash(request.form['password'])
        hash_address = generate_password_hash(request.form['address'])
        hash_card = generate_password_hash(request.form['card'])
        amount = request.form['amount']
        new_Client = Clients(email=email, fio=fio, created=created, dob=dob, id_role=role)
        db.session.add(new_Client)
        db.session.commit()
        new_Contactdetailsclients = Contactdetailsclients(id_clients=new_Client.id_clients, phone=phone,
                                                          company=company)
        new_Secretdate = Secretdate(id_clients=new_Client.id_clients, hash_password=hash_password,
                                    hash_address=hash_address)
        new_Card = Card(id_clients=new_Client.id_clients, hash_card=hash_card, amount=amount)
        db.session.add(new_Contactdetailsclients)
        db.session.add(new_Secretdate)
        db.session.add(new_Card)
        db.session.commit()

        return redirect('/login')


@app.route("/create_pok", methods=['POST', 'GET'])
@login_required
def create_pok():
    if request.method == 'GET':
        return render_template('create_pok.html')


@app.route("/create_rab", methods=['POST', 'GET'])
@login_required
def create_rab():
    if request.method == 'GET':
        return render_template('create_rab.html')


@app.route("/status")
def status():
    return {'status': 'true', 'name': 'TG', 'time': time.asctime()}


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect('/login' + '?next=' + request.url)
    return response


@manager.user_loader
def load_user(user_id):
    return Clients.query.get(user_id)


if __name__ == '__main__':
    app.run(debug=True)
