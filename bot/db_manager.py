import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def reset_events_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("DROP TABLE events;")
    cur.execute("CREATE TABLE events (name varchar, day date, desc varchar);")

    cur.close()
    conn.close()

def store_event(event_name, date, desc):
    pass

def update_event(event_name, desc):
    pass

def get_events():
    pass