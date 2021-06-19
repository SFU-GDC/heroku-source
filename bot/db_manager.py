import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def reset_events_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS events;")
    cur.execute("CREATE TABLE events (name varchar, day date, desc varchar);")

    cur.close()
    conn.close()

def remove_event(unique_event_name):
    pass

def add_event(unique_event_name, date, desc):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO events (name, day, desc) VALUES (%s, %s, %s)", (unique_event_name, date, desc))
    
    cur.close()
    conn.close()

def update_event(unique_event_name, desc):
    pass

def get_events():
    pass