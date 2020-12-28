from werkzeug.security import generate_password_hash
import psycopg2

def firstrun():
    with psycopg2.connect(dbname='cursach', user='postgres', password='password', host='localhost') as conn:
        with conn.cursor() as cur:
            cur.execute(f'''CREATE TABLE roles(
    id_role SERIAL PRIMARY KEY,
    name VARCHAR(45) NOT NULL
);

CREATE TABLE posit (
    id_position SERIAL PRIMARY KEY,
    id_role INT NOT NULL REFERENCES roles (id_role),
    job_title VARCHAR(30) NOT NULL,
    salary FLOAT NOT NULL CHECK (salary >= 0)
);

CREATE TABLE clients (
    id_clients SERIAL PRIMARY KEY,
    email VARCHAR(30) NOT NULL UNIQUE,
    FIO VARCHAR(100) NOT NULL,
    created DATE NOT NULL,
    DOB DATE NOT NULL,
    id_role INT NOT NULL REFERENCES roles (id_role)
);

CREATE TABLE contact_details_clients (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients),
    phone VARCHAR(20) NOT NULL,
    company VARCHAR(40) NOT NULL
);

CREATE TABLE secret_date (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients),
    hash_password VARCHAR(100) NOT NULL,
    hash_address VARCHAR(200) NOT NULL
);

CREATE TABLE card (
    id_clients INT PRIMARY KEY REFERENCES clients (id_clients),
    hash_card VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL CHECK (amount >= 0)
);

CREATE TABLE staff (
    id_staff SERIAL PRIMARY KEY REFERENCES clients (id_clients),
    id_position INT NOT NULL REFERENCES posit (id_position)
);

CREATE TABLE publishers (
    id_publishers SERIAL PRIMARY KEY,
    publishers_name VARCHAR(45) NOT NULL
);

CREATE TABLE books (
    id_books SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    id_publishers INT NOT NULL REFERENCES publishers (id_publishers),
    year DATE NOT NULL,
    price FLOAT NOT NULL CHECK (price > 0)
);

CREATE TABLE purchases (
    id_purchases SERIAL PRIMARY KEY,
    id_clients INT NOT NULL REFERENCES clients (id_clients),
    id_books INT NOT NULL REFERENCES books (id_books),
    date DATE NOT NULL,
    id_staff INT NOT NULL REFERENCES staff (id_staff)
);

CREATE TABLE sessions (
    id_sessions SERIAL PRIMARY KEY,
    id_clients INT NOT NULL REFERENCES clients (id_clients),
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

INSERT INTO publishers (id_publishers, publishers_name) VALUES (1, 'Просвещение, Москва'), (2, 'Новое, СПБ');

INSERT INTO posit (id_position, id_role, job_title, salary) VALUES (0, 1, 'Стажер', 3000), (1, 1,'Продавец-консультант', 12000),(2, 2,'Менеджер', 30000);

BEGIN;
INSERT INTO clients (id_clients, email, FIO, created, DOB, id_role) VALUES (0, 'urvancev-00@mail.ru', 'Danik Urvantsev', now(), '2001-01-24', 2);
INSERT INTO contact_details_clients (id_clients, phone, company) VALUES (0,'89877031111', 'Vk');
INSERT INTO secret_date (id_clients, hash_password, hash_address) VALUES\
 (0, '{generate_password_hash('123456789')}', '{generate_password_hash('Sovetsk')}');
INSERT INTO card (id_clients, hash_card, amount) VALUES (0, '{generate_password_hash('4444 4444 4444 4444')}', 10000);
INSERT INTO staff (id_staff, id_position) VALUES (0, 2);
COMMIT;''')