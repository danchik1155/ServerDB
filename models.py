from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

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


class Clients(db.Model):
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


class Contactdetailsclients(db.Model):
    __tablename__ = 'contact_details_clients'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)

    def __init__(self, email, phone, company):
        self.email = email
        self.phone = phone
        self.company = company


class Secretdate(db.Model):
    __tablename__ = 'secret_date'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    hash_password = db.Column(db.String(100), nullable=False)
    hash_address = db.Column(db.String(200), nullable=False)

    def __init__(self, hash_password, hash_addres):
        self.hash_password = hash_password
        self.hash_address = hash_addres


class Card(db.Model):
    __tablename__ = 'card'

    id_clients = db.Column(db.Integer, ForeignKey('clients.id_clients', ondelete='CASCADE'), primary_key=True)
    hash_card = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float(), nullable=False)

    def __init__(self, hash_card, amount):
        self.hash_card = hash_card
        self.amount = amount
