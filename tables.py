
from flask_table import Table, Col, LinkCol

class Users(Table):
    id_clients = Col('ID')
    email = Col('Email')
    fio = Col('FIO')
    created = Col('Created')
    dob = Col('Date of birthday')
    phone = Col('Phone')
    company = Col('Company')
    hash_password = Col('Password')
    hash_address = Col('Adress')
    hash_card = Col('Card')
    amount = Col('Amount')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))

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
    id_publishers = Col('ID издателя')
    publishers_name = Col('Издатель')