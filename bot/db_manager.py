import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def reset_events_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS \"events\";")
    # https://www.psycopg.org/docs/usage.html#adaptation-of-python-values-to-sql-types
    cur.execute("CREATE TABLE \"events\" (name VARCHAR(256) UNIQUE, datetime TIMESTAMP, description VARCHAR(1024));")

    cur.close()
    conn.close()

def remove_event(unique_event_name):
    pass

def add_event(unique_event_name, date, desc):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    #(name, datetime, description)
    cur.execute("INSERT INTO \"events\" VALUES (%s, %s, %s)", (unique_event_name, date, desc))
    
    cur.close()
    conn.close()

def update_event(unique_event_name, desc):
    pass

def get_events():
    pass