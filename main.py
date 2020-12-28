import time
import psycopg2

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Clients, Contactdetailsclients, Secretdate, Card, Roles, Posit, Publishers, Purchases, Books, \
    Staff
from models import UsersBookTable, BooksTable, PublishersTable
from FirstRunning import firstrun

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:qetuosfhk@localhost:5432/cursach"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'so so very very secret'
db.init_app(app)
manager = LoginManager(app)
psycopglog = 'editor'
psycopgpass = 'qsefthuko'


@app.route('/')
def index():
    return redirect('/login')


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
            with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
                with conn.cursor() as cur:
                    cur.execute(f"INSERT INTO sessions (id_clients, session_date) "
                                f"VALUES ({current_user.id_clients},"
                                f"'{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}');")
                    conn.commit()
            next_page = request.args.get('next')
            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect('/cabinet')
        else:
            flash('Login or password is not correct')
    return render_template('login.html')


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    if request.method == 'POST':
        fio = request.form['fio']
        created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
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


@app.route("/cabinet", methods=['POST', 'GET'])
@login_required
def cabinet():
    if request.method == 'GET':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute(f"SELECT id_clients, id_purchases, name, publishers_name, year, date FROM purchases inner join books \
                on books.id_books=purchases.id_books inner join publishers \
                on publishers.id_publishers=books.id_publishers where id_clients = {current_user.id_clients};")
                items = cur.fetchall()
                conn.commit()
        iitems = []
        for i in range(len(items)):
            iitems.append(dict(id_clients=items[i][0], id_purchases=items[i][1], name=items[i][2],
                               publishers_name=items[i][3], year=items[i][4], date=items[i][5]))
        table = UsersBookTable(iitems)
        if db.session.query(Staff).filter_by(id_staff=current_user.id_clients).first():
            salary = db.session.query(Posit).filter_by(id_position=db.session.query(Staff).filter_by(
                id_staff=current_user.id_clients).first().id_position).first().salary
            job_title = db.session.query(Posit).filter_by(id_position=db.session.query(Staff).filter_by(
                id_staff=current_user.id_clients).first().id_position).first().job_title
        else:
            salary = 0
            job_title = ''
        return render_template('cabinet.html', fio=current_user.fio,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name,
                               amount=db.session.query(Card).filter_by(
                                   id_clients=current_user.id_clients).first().amount,
                               book=table,
                               salary=salary,
                               job_title=job_title)


@app.route("/sale", methods=['POST', 'GET'])
@login_required
def sale():
    if request.method == 'GET':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute(f"SELECT id_books, name, publishers_name, year, price FROM books inner join publishers \
                       on books.id_publishers=publishers.id_publishers;")
                items = cur.fetchall()
                conn.commit()
        iitems = []
        for i in range(len(items)):
            iitems.append(dict(id_books=items[i][0], name=items[i][1], publishers_name=items[i][2], year=items[i][3],
                               price=items[i][4]))
        table = BooksTable(iitems)
        return render_template('sale.html', fio=current_user.fio, сatalog=table)
    if request.method == 'POST':
        id_books = request.form['id_books']
        date = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
        id_clients = db.session.query(Clients).filter_by(email=request.form['email']).first().id_clients
        price = db.session.query(Books).filter_by(id_books=id_books).first().price
        new_Purchases = Purchases(id_books=id_books, id_clients=id_clients,
                                  id_staff=current_user.id_clients, date=date)
        db.session.add(new_Purchases)
        db.session.commit()
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute("UPDATE card set amount = amount - {} where id_clients = {}".format(price, id_clients))
                cur.execute("UPDATE card set amount = amount + {} where id_clients = {}".format(price, 0))
                conn.commit()
        return redirect('/login')


@app.route("/book", methods=['POST', 'GET'])
def book():
    if request.method == 'GET':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute(f"SELECT  id_publishers, publishers_name from publishers;")
                items = cur.fetchall()
                conn.commit()
        iitems = []
        for i in range(len(items)):
            iitems.append(dict(id_publishers=items[i][0], publishers_name=items[i][1]))
        table = PublishersTable(iitems)
        return render_template('book.html', сatalog_isd=table)
    if request.method == 'POST':
        name = request.form['name']
        id_publishers = request.form['id_publisher']
        year = request.form['year']
        price = request.form['price']
        new_Book = Books(name=name, id_publishers=id_publishers, year=year, price=price)
        db.session.add(new_Book)
        db.session.commit()
        return redirect('/login')


@app.route("/publisher", methods=['POST', 'GET'])
@login_required
def publisher_pg():
    if request.method == 'POST':
        publishers_name = request.form['publisher']
        new_Publisher = Publishers(publishers_name=publishers_name)
        db.session.add(new_Publisher)
        db.session.commit()
        return redirect('/login')


@app.route("/create_pok", methods=['POST', 'GET'])
@login_required
def create_pok():
    if request.method == 'GET':
        return render_template('create_pok.html')
    if request.method == 'POST':
        fio = request.form['fio']
        created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
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


@app.route("/create_rab", methods=['POST', 'GET'])
@login_required
def create_rab():
    if request.method == 'GET':
        return render_template('create_rab.html')
    if request.method == 'POST':
        fio = request.form['fio']
        created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
        dob = request.form['dob']
        if request.form['role'] == 'Стажер':
            role = 1
            id_position = 0
        elif request.form['role'] == 'Продавец-консультант':
            role = 1
            id_position = 1
        elif request.form['role'] == 'Менеджер':
            role = 2
            id_position = 2

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
        new_Staff = Staff(id_staff=new_Client.id_clients, id_position=id_position)
        db.session.add(new_Contactdetailsclients)
        db.session.add(new_Secretdate)
        db.session.add(new_Card)
        db.session.add(new_Staff)
        db.session.commit()
        return redirect('/login')


@app.route("/del", methods=['POST', 'GET'])
@login_required
def deletebook():
    if request.method == 'GET':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute(f"SELECT id_books, name, publishers_name, year, price FROM books inner join publishers \
                       on books.id_publishers=publishers.id_publishers;")
                items = cur.fetchall()
                conn.commit()
        iitems = []
        for i in range(len(items)):
            iitems.append(dict(id_books=items[i][0], name=items[i][1], publishers_name=items[i][2], year=items[i][3],
                               price=items[i][4]))
        table = BooksTable(iitems)
        return render_template('del.html', сatalog=table)
    if request.method == 'POST':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM books where id_books = {};".format(request.form['id_books']))
        return redirect('/login')


@app.route('/form')
def form():
    # with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
    #     # Open a cursor to perform database operations
    #     with conn.cursor() as cur:
    #         cur.execute(f"SELECT id_purchases, name, publishers_name, year, date FROM purchases inner join books \
    #         on books.id_books=purchases.id_books inner join publishers \
    #         on publishers.id_publisher=publishers.id_publisher where id_clients = {current_user.id_clients};")
    #         items = cur.fetchall()
    #         conn.commit()
    # iitems = []
    # for i in range(len(items)):
    #     iitems.append(dict(id_purchases=items[i][0], name=items[i][1],
    #                        publishers_name=items[i][2], year=items[i][3], date=items[i][3]))
    # table = UsersBookTable(iitems)
    with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(f"SELECT clients.id_clients, fio, amount FROM clients inner join card \
            on clients.id_clients=card.id_clients;")
            items = cur.fetchall()
            conn.commit()
    iitems = []
    for i in range(len(items)):
        iitems.append(
            dict(id_clients=items[i][0], id_purchases=items[i][1], name=items[i][2], publishers_name='-', year='-',
                 date='-'))
    table = UsersBookTable(iitems)
    return render_template("form.html", table=table)


@app.route('/users')
def users():
    pass

    #
    # with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
    #     # Open a cursor to perform database operations
    #     with conn.cursor() as cur:
    #         cur.execute(f"SELECT id_books, name, publishers_name, year, price FROM books inner join publishers \
    #                on books.id_publishers=publishers.id_publishers;")
    #         items = cur.fetchall()
    #         conn.commit()
    # iitems = []
    # for i in range(len(items)):
    #     iitems.append(dict(name=items[i][0], publishers_name=items[i][1], year=items[i][2], date=items[i][3]))


@app.route("/status")
def status():
    return {'status': 'true', 'name': 'TG', 'time': time.asctime()}


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE sessions SET session_logout = "
                        f"'{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}' "
                        f"WHERE id_clients={current_user.id_clients}")
            conn.commit()
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
    try:
        firstrun()
    except psycopg2.errors.DuplicateTable:
        pass
    app.run(debug=True)
