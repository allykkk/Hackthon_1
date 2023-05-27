import json
import logging
import sqlite3
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def get_ready_db_connection():
    conn = sqlite3.connect('reminder.db')
    cursor = conn.cursor()

    create_table_query = '''
            CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY,
                       chat_id INTEGER NOT NULL,
                       subject TEXT,
                       event TEXT NOT NULL,
                       date TEXT NOT NULL,
                       enumerated TEXT NOT NULL,
                       more_info TEXT) '''

    logging.info("CREATE TABLE IF NOT EXISTS ...")
    cursor.execute(create_table_query)

    logging.info("Success!")
    conn.commit()

    return conn


def safe_db_connection(max_attempts=10):
    # Try this max_attempts times, if you fail then return false.
    for _ in range(max_attempts):
        try:
            logging.info("Trying to connect to DB")
            # Function should either return False or exception...
            conn = get_ready_db_connection()
            if conn:
                return conn
        except:
            pass
    return None


def insert_data(parsed_message):
    conn = safe_db_connection()
    cursor = conn.cursor()

    insert_query = '''INSERT INTO events 
                            (chat_id,subject, event, date, enumerated, more_info) 
                            VALUES (?, ?, ?, ?, ?, ?) '''

    logging.info(f"Inserting into DB event: {json.dumps(parsed_message)}")
    cursor.execute(insert_query, (parsed_message['chat_id'],
                                  parsed_message['subject'], parsed_message['event'], parsed_message['date'],
                                  parsed_message['enumerated'],
                                  parsed_message['more_info']))
    conn.commit()
    logging.info("Closing DB")
    conn.close()


def get_column_names(cursor):
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchone()
    if rows:
        return [desc[0] for desc in cursor.description]
    else:
        return []




# Function to perform the scanning operation
def scan_database(remind_days: list):
    # Connect to the database
    conn = safe_db_connection()
    cursor = conn.cursor()
    # Get today's date
    today = datetime.date.today()
    # Get the date we need to remind the event
    returned_data = {}
    column_names = get_column_names(cursor)
    for day in remind_days:
        target_date = today + datetime.timedelta(days=day)
        # Format the target date as string in "%m-%d" format
        target_date = target_date.strftime("%m-%d")
        # Retrieve items from the database with the same date as target date
        cursor.execute("SELECT * FROM events WHERE date = ?", (target_date,))
        rows = cursor.fetchall()
        # Fetch the results
        rows_list = []
        for row in rows:
            # each row's data stored as dict.
            row_dict = {}
            for i, names in enumerate(column_names):
                row_dict[names] = row[i]
            # if one date has multiple rows result, put them in a list
            rows_list.append(row_dict)
        # final format is a dict with day as key and value is list contains row/rows in a format of dictionary
        returned_data[day] = rows_list
    conn.close()
    return returned_data



