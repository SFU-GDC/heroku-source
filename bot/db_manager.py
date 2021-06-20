import os
from datetime import datetime
import psycopg2

# TODO: 
#  modify this so that it uses a discord channel as a db.
#

DATABASE_URL = os.environ.get('DATABASE_URL')


def reset_events_table():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        # https://www.psycopg.org/docs/usage.html#adaptation-of-python-values-to-sql-types
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE, datetime TIMESTAMP, description VARCHAR(1024), metadata VARCHAR(1024) DEFAULT 'empty')")
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

    #cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE);") #, datetime TIMESTAMP, description VARCHAR(1024));")

def remove_event(unique_event_name):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("DELETE FROM events WHERE name = (%s)", [unique_event_name])
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)
    
def add_event(unique_event_name, date, desc):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("INSERT INTO events (name, datetime, description) VALUES (%s, %s, %s)", (unique_event_name, date, desc))
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

def update_event(unique_event_name, desc, metadata):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("UPDATE events SET description = (%s), metadata = (%s) WHERE name = (%s)", (desc, metadata, unique_event_name))
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

def get_all_events():
    ret_val = None

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM events")
        ret_val = cur.fetchall()
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

    return ret_val

def get_next_events(n):
    ret_val = []

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM events WHERE datetime > (%s) ORDER BY datetime ASC", [datetime.now()])
        ret_val = cur.fetchmany(n)

        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

    return ret_val

# -----------------------------------------
# Util:

def close_connection(conn):
    if conn is not None:
        conn.commit()
        conn.close()
        print('Database connection closed')