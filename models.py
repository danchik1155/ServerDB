from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class UsersBookTable(Table):
    id_clients = Col('ID', show=False)
    id_purchases = Col('Номер сделки')
    name = Col('Название книги')
    publishers_name = Col('Издатель')
    year = Col('Дата издания')
    date = Col('Дата покупки')

class BooksTable(Table):
    id_books = Col('ID Книги')
    name = Col('Название книги')
    publishers_name = Col('Издатель')
    year = Col('Дата издания')
    price = Col('Цена')

class PublishersTable(Table):
    id_publisher = Col('ID издателя')
    publishers_name = Col('Издатель')

class Roles(db.Model):
    __tablename__ = 'roles'

    id_role = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

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
    id_role = db.Column(db.Integer, ForeignKey('roles.id_role', ondelete='CASCADE'), nullable=False, unique=True)

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
