import time
import psycopg2

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from Crypto.Cipher import Salsa20

from models import db, Clients, Contactdetailsclients, Secretdate, Card, Roles, Posit, Publishers, Purchases, Books, \
    Staff
from tables import UsersBookTable, BooksTable, PublishersTable, Users
from FirstRunning import firstrun

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:qetuosfhk@localhost:5432/cursach"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'so so very very secret'

secret = b'*Thirty-two byte (256 bits) key*'
cipher = Salsa20.new(key=secret)

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
        user = db.session.query(Clients).filter_by(email=login).first()
        if user and check_password_hash(
                db.session.query(Secretdate).filter_by(id_clients=user.id_clients).first().hash_password, password):
            login_user(user)
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
        cipher = Salsa20.new(key=secret)
        fio = request.form['fio']
        created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
        dob = request.form['dob']  # определить формат
        role = 0
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        hash_password = generate_password_hash(request.form['password'])
        print(hash_password)
        hash_address = generate_password_hash(request.form['address'])
        hash_card = cipher.nonce + cipher.encrypt(bytes(request.form['card'], 'utf-8'))
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
        table.border = True
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
                               # amount=db.session.query(Card).filter_by(
                               #    id_clients=current_user.id_clients).first().amount,
                               amount=db.session.query(Card).filter_by(
                                   id_clients=current_user.id_clients).first().amount,
                               book=table,
                               salary=salary,
                               job_title=job_title)


@app.route("/money", methods=['POST', 'GET'])
@login_required
def money():
    if request.method == 'POST':
        amount = request.form['money']
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute("UPDATE card set amount = amount + %f where id_clients = %s;" %
                            (float(amount), current_user.id_clients))
                conn.commit()
        return redirect('/cabinet')
    else:
        return 'What are you doing here?'


@app.route("/sale", methods=['POST', 'GET'])
@login_required
def sale():
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Продавец" and \
            db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
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
    if request.method == 'GET':
        return render_template('sale.html', fio=current_user.fio, сatalog=table,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
    if request.method == 'POST':
        id_books = request.form['id_books']
        if db.session.query(Books).filter_by(id_books=id_books).first() is not None:
            price = db.session.query(Books).filter_by(id_books=id_books).first().price
        else:
            price = 0
        return render_template('sale.html', id_books=id_books, fio=current_user.fio, сatalog=table,
                               price=price,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)


@app.route("/book", methods=['POST', 'GET'])
@login_required
def book():
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Продавец" and \
            db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
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
        table.border = True
        return render_template('book.html', сatalog_isd=table,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
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
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Продавец" and \
            db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
    if request.method == 'POST':
        publishers_name = request.form['publisher']
        new_Publisher = Publishers(publishers_name=publishers_name)
        db.session.add(new_Publisher)
        db.session.commit()
        return redirect('/login')
    else:
        return 'What are you doing here?'


@app.route("/create_pok", methods=['POST', 'GET'])
@login_required
def create_pok():
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Продавец" and \
            db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
    if request.method == 'GET':
        return render_template('create_pok.html',
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
    if request.method == 'POST':
        cipher = Salsa20.new(key=secret)
        fio = request.form['fio']
        created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
        dob = request.form['dob']  # определить формат
        role = 0
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        hash_password = generate_password_hash(request.form['password'])
        hash_address = generate_password_hash(request.form['address'])
        hash_card = cipher.nonce + cipher.encrypt(bytes(request.form['card'], 'utf-8'))
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
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
    if request.method == 'GET':
        return render_template('create_rab.html',
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
    if request.method == 'POST':
        cipher = Salsa20.new(key=secret)
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
        hash_card = cipher.nonce + cipher.encrypt(bytes(request.form['card'], 'utf-8'))
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
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
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
        table.border = True
        return render_template('del.html', сatalog=table,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
    if request.method == 'POST':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM books where id_books = {};".format(request.form['id_books']))
        return redirect('/login')


@app.route("/search", methods=['POST', 'GET'])
@login_required
def search_pg():
    id_books = request.form['id_books']
    if request.method == 'POST':
        with psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost') as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                cur.execute(f"SELECT id_books, name, publishers_name, year, price FROM books inner join publishers \
                       on books.id_publishers=publishers.id_publishers where id_books={id_books};")
                items = cur.fetchall()
                conn.commit()
        iitems = []
        for i in range(len(items)):
            iitems.append(dict(id_books=items[i][0], name=items[i][1], publishers_name=items[i][2], year=items[i][3],
                               price=items[i][4]))
        table = BooksTable(iitems)
        table.border = True
        return render_template('sale.html', search=table,
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)
    else:
        return 'What are you doing here?'


@app.route('/all', methods=['POST', 'GET'])
def users():
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Clients.id_clients, Clients.email, Clients.fio, Clients.created, Clients.dob,
                             Contactdetailsclients.phone, Contactdetailsclients.company).join(
        Contactdetailsclients, Clients.id_clients == Contactdetailsclients.id_clients).paginate(page=page, per_page=5)
    table = Users(db.session.query(Clients.id_clients, Clients.email, Clients.fio, Clients.created, Clients.dob,
                                   Contactdetailsclients.phone, Contactdetailsclients.company).join(
        Contactdetailsclients, Clients.id_clients == Contactdetailsclients.id_clients).paginate(page=page,
                                                                                                per_page=5).items)
    table.border = True
    return render_template('all.html', pols=table, posts=posts,
                           role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name)


@app.route("/edit/<int:id_clients>", methods=['POST', 'GET'])
def edit(id_clients):
    if db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name != "Менеджер":
        return 'What are you doing here?'
    if request.method == 'GET':
        cipher = Salsa20.new(key=secret)
        msg = eval(db.session.query(Card).filter_by(id_clients=id_clients).first().hash_card)
        print(msg)
        msg_nonce = msg[:8]
        ciphertext = msg[8:]
        print(msg_nonce)
        cipher = Salsa20.new(key=secret, nonce=msg_nonce)
        plaintext = cipher.decrypt(ciphertext).decode('ascii')
        print(plaintext)
        return render_template('edit.html',
                               role=db.session.query(Roles).filter_by(id_role=current_user.id_role).first().name,
                               id_clients=id_clients,
                               email=db.session.query(Clients).filter_by(id_clients=id_clients).first().email,
                               fio=db.session.query(Clients).filter_by(id_clients=id_clients).first().fio,
                               created=db.session.query(Clients).filter_by(id_clients=id_clients).first().created,
                               dob=db.session.query(Clients).filter_by(id_clients=id_clients).first().dob,
                               phone=db.session.query(Contactdetailsclients).filter_by(
                                   id_clients=id_clients).first().phone,
                               company=db.session.query(Contactdetailsclients).filter_by(
                                   id_clients=id_clients).first().company,
                               password='*',
                               address=db.session.query(Secretdate).filter_by(
                                   id_clients=id_clients).first().hash_address,
                               card=plaintext,
                               amount=db.session.query(Card).filter_by(id_clients=id_clients).first().amount)
    else:
        return 'What are you doing here?'


@app.route("/edit2", methods=['POST', 'GET'])
def edit2():
    cipher = Salsa20.new(key=secret)
    fio = request.form['fio']
    created = time.strftime('%d/%m/%Y', time.localtime())  # использовать дату
    dob = request.form['dob']  # определить формат
    role = 0
    id_clients = request.form['id_clients']
    email = request.form['email']
    phone = request.form['phone']
    company = request.form['company']
    hash_address = generate_password_hash(request.form['address'])
    hash_card = cipher.nonce + cipher.encrypt(bytes(request.form['card'], 'utf-8'))
    amount = request.form['amount']
    new_Client = Clients.query.filter_by(id_clients=id_clients).first()
    new_Client.email = email
    new_Client.fio = fio
    new_Client.created = created
    db.session.commit()

    new_Contactdetailsclients = Contactdetailsclients.query.filter_by(id_clients=id_clients).first()
    new_Contactdetailsclients.phone = phone
    new_Contactdetailsclients.company = company
    new_Secretdate = Secretdate.query.filter_by(id_clients=id_clients).first()
    new_Secretdate.hash_address = hash_address
    new_Card = Card.query.filter_by(id_clients=id_clients).first()
    new_Card.hash_card = hash_card
    new_Card.amount = amount
    db.session.commit()
    return redirect('/all')


@app.route("/status")
def status():
    return {'status': 'true', 'name': 'TG', 'time': time.asctime()}


@app.route('/id_books', methods=['GET', 'POST'])
@login_required
def idbook():
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
            with conn.cursor() as cur:
                cur.execute("UPDATE card set amount = amount - {} where id_clients = {}".format(price, id_clients))
                cur.execute("UPDATE card set amount = amount + {} where id_clients = {}".format(price, 0))
                conn.commit()
        return redirect('/login')
    else:
        return 'What are you doing here?'


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
