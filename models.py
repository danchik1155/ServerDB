from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

# from main import manager

db = SQLAlchemy()


class InfoModel(db.Model):
    __tablename__ = 'info_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    age = db.Column(db.Integer())

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"{self.name}:{self.age}"


class Clients(db.Model, UserMixin):
    __tablename__ = 'clients'

    id_clients = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(100), nullable=False)
    created = db.Column(db.Date(), nullable=False)
    dob = db.Column(db.Date(), nullable=False)
    id_role = db.Column(db.Integer, ForeignKey('role.id_role', ondelete='CASCADE'), nullable=False, unique=True)

    def __init__(self, fio, created, dob, id_role):
        self.fio = fio
        self.created = created
        self.dob = dob
        self.id_role = id_role

    def gett_id(self):
        return self.query.get(self.id_clients)


class Contactdetailsclients(db.Model):
    __tablename__ = 'contact_details_clients'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)

    def __init__(self, id_clients, email, phone, company):
        self.id_clients = id_clients
        self.email = email
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
