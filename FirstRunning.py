from werkzeug.security import generate_password_hash
import psycopg2
from Crypto.Cipher import Salsa20

secret = b'*Thirty-two byte (256 bits) key*'
cipher = Salsa20.new(key=secret)

def firstrun():
    with psycopg2.connect(dbname='cursach', user='moderator', password='wryipadgjl', host='localhost') as conn:
        with conn.cursor() as cur:
            cur.execute(f'''CREATE TABLE roles(
    id_role SERIAL PRIMARY KEY,
    name VARCHAR(45) NOT NULL
);

CREATE TABLE posit (
    id_position SERIAL PRIMARY KEY,
    id_role INT NOT NULL REFERENCES roles (id_role),
    job_title VARCHAR(100) NOT NULL,
    salary FLOAT NOT NULL CHECK (salary >= 0)
);

CREATE TABLE clients (
    id_clients SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    FIO VARCHAR(100) NOT NULL,
    created DATE NOT NULL,
    DOB DATE,
    id_role INT NOT NULL REFERENCES roles (id_role) ON DELETE CASCADE
);

CREATE INDEX mailindex on clients USING hash (email);

CREATE TABLE contact_details_clients (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients) ON DELETE CASCADE,
    phone VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL
);

CREATE TABLE secret_date (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients) ON DELETE CASCADE,
    hash_password VARCHAR(100) NOT NULL,
    hash_address VARCHAR(200) NOT NULL
);

CREATE TABLE card (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients) ON DELETE CASCADE,
    hash_card TEXT NOT NULL,
    amount FLOAT NOT NULL CHECK (amount >= 0)
);

CREATE TABLE staff (
    id_staff SERIAL PRIMARY KEY REFERENCES clients (id_clients) ON DELETE CASCADE,
    id_position INT NOT NULL REFERENCES posit (id_position) ON DELETE CASCADE
);

CREATE TABLE publishers (
    id_publishers SERIAL PRIMARY KEY,
    publishers_name VARCHAR(45) NOT NULL
);

CREATE TABLE books (
    id_books SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    id_publishers INT NOT NULL REFERENCES publishers (id_publishers) ON DELETE CASCADE,
    year DATE NOT NULL,
    price FLOAT NOT NULL CHECK (price > 0)
);

CREATE TABLE purchases (
    id_purchases SERIAL PRIMARY KEY,
    id_clients INT NOT NULL REFERENCES clients (id_clients) ON DELETE CASCADE,
    id_books INT NOT NULL REFERENCES books (id_books) ON DELETE CASCADE,
    date DATE NOT NULL,
    id_staff INT NOT NULL REFERENCES staff (id_staff) ON DELETE CASCADE
);

CREATE TABLE sessions (
    id_sessions SERIAL PRIMARY KEY,
    id_clients INT NOT NULL REFERENCES clients (id_clients) ON DELETE CASCADE,
    session_date TIMESTAMP NOT NULL,
    session_logout TIMESTAMP
);

CREATE TABLE deleted_books (
    id_deleted_books SERIAL PRIMARY KEY,
    id_books INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    id_publishers INT NOT NULL,
    year DATE NOT NULL,
    price FLOAT NOT NULL
);

CREATE FUNCTION deleted_book() RETURNS trigger AS $deleted_book$
    BEGIN
        INSERT INTO deleted_books( id_books, name,  id_publishers, year, price) values (OLD.id_books, OLD.name,  OLD.id_publishers, OLD.year, OLD.price);
        RETURN OLD;
    END;
$deleted_book$ LANGUAGE plpgsql;

CREATE TRIGGER deleted_book BEFORE DELETE ON books
    FOR EACH ROW EXECUTE PROCEDURE deleted_book();

INSERT INTO roles (id_role, name) VALUES (0, 'Покупатель'), (1, 'Продавец'), (2, 'Менеджер');

ALTER SEQUENCE roles_id_role_seq START WITH 3;

INSERT INTO publishers (publishers_name) VALUES ('Просвещение, Москва'), ('Новое, СПБ');

INSERT INTO posit (id_position, id_role, job_title, salary) VALUES (0, 1, 'Стажер', 3000), (1, 1,'Продавец-консультант', 12000),(2, 2,'Менеджер', 30000);

ALTER SEQUENCE posit_id_position_seq START WITH 3;

INSERT INTO clients (id_clients, email, FIO, created, DOB, id_role) VALUES (0, 'urvancev-00@mail.ru', 'Danik Urvantsev', now(), '2001-01-24', 2);
INSERT INTO contact_details_clients (id_clients, phone, company) VALUES (0,'89877031111', 'Vk');
INSERT INTO secret_date (id_clients, hash_password, hash_address) VALUES\
 (0, '{generate_password_hash('Danilka1122')}', 'Sovetsk');''')

            cur.execute(
                "INSERT INTO card(id_clients, hash_card, amount) VALUES (%s,%s,%s);" %
                (0, cipher.nonce + cipher.encrypt(bytes('4444-4444-4444-4444', 'utf-8')), 10000))

            cur.execute('''
INSERT INTO staff (id_staff, id_position) VALUES (0, 2);
GRANT ALL PRIVILEGES on all tables in schema public to editor;
GRANT ALL PRIVILEGES on all sequences in schema public to editor;''')
        conn.commit()

