import csv
import time
import traceback

import email.utils
from sqlite3 import IntegrityError

from threading import Thread
import psycopg2
from werkzeug.security import generate_password_hash
from Crypto.Cipher import Salsa20

secret = b'*Thirty-two byte (256 bits) key*'
cipher = Salsa20.new(key=secret)

psycopglog = 'moderator'
psycopgpass = 'wryipadgjl'





def import_sect(line_count, psycopglog, psycopgpass):
    conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
    cur = conn.cursor()
    with open('table1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            line_count += 1
            p_id = line_count
            cur.execute("insert into secret_date(id_clients, hash_password, hash_address) VALUES (%s,%s,%s);"
                        , (p_id, generate_password_hash(row[3]), row[1]))

            conn.commit()

            print(f'Processed table1 {line_count} lines.')
    conn.commit()
    conn.autocommit = True

def import_table1(line_count, psycopglog, psycopgpass):
    conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
    cur = conn.cursor()
    with open('table1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            line_count += 1
            p_id = line_count
            try:
                rfc_date = email.utils.parsedate_to_datetime(row[4]).isoformat()
            except:
                rfc_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            try:
                cur.execute("insert into clients(id_clients, FIO, email, created, id_role) VALUES (%s,%s,%s,%s,0)",
                            (p_id, row[0], row[2], rfc_date))
            except psycopg2.Error as e:
                conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
                cur = conn.cursor()
                cur.execute("insert into clients(id_clients, FIO, email, created, id_role) VALUES (%s,%s,%s,%s,0)",
                            (p_id, row[0], row[2] + str(p_id), rfc_date))


            conn.commit()

            print(f'Processed table1 {line_count} lines.')
    conn.commit()
    conn.autocommit = True


def import_table2(line_count, psycopglog, psycopgpass):
    conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
    cur = conn.cursor()
    with open('table2') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            line_count += 1
            p_id = line_count
            try:
                rfc_date = email.utils.parsedate_to_datetime(row[2]).isoformat()
            except:
                rfc_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            cur.execute(
                "insert into contact_details_clients(id_clients, phone, company) VALUES (%s,%s,%s);"
                , (p_id, row[4], row[5]))
            cur.execute(
                "update clients set DOB = %s where id_clients = %s ;"
                , (rfc_date, p_id))
            if line_count % 200 == 0:
                conn.commit()
            print(f'Processed table2 {line_count} lines.')
    conn.commit()
    conn.autocommit = True


def import_table3(line_count, psycopglog, psycopgpass):
    conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
    cur = conn.cursor()
    with open('table3') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            line_count += 1
            p_id = line_count
            try:
                cur.execute(
                    "insert into card(id_clients, hash_card, amount) VALUES (%s,%s,%s);"
                    , (p_id, cipher.nonce + cipher.encrypt(bytes(row[2], 'utf-8')), row[3]))
            except psycopg2.Error as e:
                conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
                cur = conn.cursor()
                cur.execute(
                    "insert into card(id_clients, hash_card, amount) VALUES (%s,%s,%s);"
                    , (p_id, cipher.nonce + cipher.encrypt(bytes(row[3], 'utf-8')), row[4]))

            conn.commit()
            print(f'Processed table3 {line_count} lines.')
    conn.commit()
    conn.autocommit = True


if __name__ == '__main__':
    conn = psycopg2.connect(dbname='cursach', user=psycopglog, password=psycopgpass, host='localhost')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO card(id_clients, hash_card, amount) VALUES (%s,%s,%s);"
        , (0, cipher.nonce + cipher.encrypt(bytes('4444-4444-4444-4444', 'utf-8')), 10000))
    conn.commit()
    print(f'Processed table3 0 lines.')
    import_table3(0, psycopglog, psycopgpass)