from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Posit(db.Model):
    __tablename__ = 'posit'

    id_position = db.Column(db.Integer(), primary_key=True)
    id_role = db.Column(db.Integer(), ForeignKey('roles.id_role', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(30), nullable=False)
    salary = db.Column(db.Float(), nullable=False)

    def __init__(self, id_role, job_title, salary):
        self.id_role = id_role
        self.job_title = job_title
        self.salary = salary

class Publishers(db.Model):
    __tablename__ = 'publishers'

    id_publishers = db.Column(db.Integer(), primary_key=True)
    publishers_name = db.Column(db.String(45), nullable=False)

    def __init__(self, publishers_name):
        self.publishers_name = publishers_name

class Books(db.Model):
    __tablename__ = 'books'

    id_books = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, )
    id_publishers = db.Column(db.Integer(), ForeignKey('publishers.id_publishers', ondelete='CASCADE'),
                              nullable=False, )
    year = db.Column(db.Date(), nullable=False, )
    price = db.Column(db.Float(), nullable=False, )

    def __init__(self, name, id_publishers, year, price):
        self.name = name
        self.id_publishers = id_publishers
        self.year = year
        self.price = price

class Purchases(db.Model):
    __tablename__ = 'purchases'

    id_purchases = db.Column(db.Integer(), primary_key=True)
    id_clients = db.Column(db.Integer(), ForeignKey('clients.id_clients', ondelete='CASCADE'), nullable=False, )
    id_books = db.Column(db.Integer(), ForeignKey('books.id_books', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    id_staff = db.Column(db.Integer(), ForeignKey('staff.id_staff', ondelete='CASCADE'), nullable=False)

    def __init__(self, id_clients, id_books, date, id_staff):
        self.id_clients = id_clients
        self.id_books = id_books
        self.date = date
        self.id_staff = id_staff


class Staff(db.Model):
    __tablename__ = 'staff'

    id_staff = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    id_position = db.Column(db.Integer, nullable=False)

    def __init__(self, id_staff, id_position):
        self.id_staff = id_staff
        self.id_position = id_position


class Roles(db.Model):
    __tablename__ = 'roles'

    id_role = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('Clients', backref='author', lazy='dynamic')

    def __init__(self, id_role, name):
        self.id_role = id_role
        self.name = name


class Clients(db.Model, UserMixin):
    __tablename__ = 'clients'

    id_clients = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    fio = db.Column(db.String(100), nullable=False)
    created = db.Column(db.Date(), nullable=False)
    dob = db.Column(db.Date(), nullable=False)
    id_role = db.Column(db.Integer, ForeignKey('roles.id_role', ondelete='CASCADE'), nullable=False)

    def __init__(self, email, fio, created, dob, id_role):
        self.email = email
        self.fio = fio
        self.created = created
        self.dob = dob
        self.id_role = id_role

    def get_id(self):
        return (self.id_clients)


class Contactdetailsclients(db.Model):
    __tablename__ = 'contact_details_clients'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    phone = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)

    def __init__(self, id_clients, phone, company):
        self.id_clients = id_clients
        self.phone = phone
        self.company = company


class Secretdate(db.Model):
    __tablename__ = 'secret_date'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    hash_password = db.Column(db.String(100), nullable=False)
    hash_address = db.Column(db.String(200), nullable=False)

    def __init__(self, id_clients, hash_password, hash_address):
        self.id_clients = id_clients
        self.hash_password = hash_password
        self.hash_address = hash_address


class Card(db.Model):
    __tablename__ = 'card'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    hash_card = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float(), nullable=False)

    def __init__(self, id_clients, hash_card, amount):
        self.id_clients = id_clients
        self.hash_card = hash_card
        self.amount = amount
