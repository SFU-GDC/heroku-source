import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')


def reset_events_table():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        conn.autocommit = 1

        cur = conn.cursor()
        cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE)") #, datetime TIMESTAMP, description VARCHAR(1024));")
        cur.close()
    except Exception as error:
        print('Could not connect to the Database.')
        print('Cause: {}'.format(error))

    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


    #cur.execute("DROP TABLE IF EXISTS \"events\";")
    # https://www.psycopg.org/docs/usage.html#adaptation-of-python-values-to-sql-types
    #cur.execute("CREATE TABLE events (name VARCHAR(255) UNIQUE);") #, datetime TIMESTAMP, description VARCHAR(1024));")

def remove_event(unique_event_name):
    pass

def add_event(unique_event_name, date, desc):
    conn = None
    print("INSERT INTO events VALUES ({})".format(unique_event_name)) #, %s, %s)", (unique_event_name, date, desc))
    try:
        conn = psycopg2.connect(DATABASE_URL) # , sslmode='require'
        conn.autocommit = 1

        cur = conn.cursor()
        cur.execute("CREATE TABLE events (name VARCHAR(255))")
        cur.execute("INSERT INTO events (name) VALUES (%s)", ["meeting"]) #, %s, %s)", (unique_event_name, date, desc))
        cur.close()
    except Exception as error:
        print('Could not connect to the Database.')
        print('Cause: {}'.format(error))

    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    #(name, datetime, description)
    

def update_event(unique_event_name, desc):
    pass

def get_events():
    pass