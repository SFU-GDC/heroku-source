import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')


def reset_events_table():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        # https://www.psycopg.org/docs/usage.html#adaptation-of-python-values-to-sql-types
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE, datetime TIMESTAMP, description VARCHAR(1024))")
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

    #cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE);") #, datetime TIMESTAMP, description VARCHAR(1024));")

def remove_event(unique_event_name):
    pass

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

def update_event(unique_event_name, desc):
    pass

def get_events():
    ret_val = None

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM events;")
        ret_val = cur.fetchall()
        
        cur.close()
    except Exception as error:
        print('Could not connect to the Database: {}'.format(error))

    finally:
        close_connection(conn)

    return ret_val

def close_connection(conn):
    if conn is not None:
        conn.commit()
        conn.close()
        print('Database connection closed')