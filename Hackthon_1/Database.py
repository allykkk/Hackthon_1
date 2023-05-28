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
    # date is text in db instead of date because sqlite required year as well - which does not apply to the project
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
def scan_database(remind_days: list):  # make sure list[0] is today
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
            row_dict = {}
            for i, names in enumerate(column_names):
                row_dict[names] = row[i]
            rows_list.append(row_dict)

            # If today is the day for this event, let's either remove it or update it to the next month
            if day == 0:
                check_onetime_event(row_dict, conn)
                check_monthly_event(row_dict, conn)
        returned_data[day] = rows_list
    # print(returned_data)
    conn.close()
    return returned_data


# row data is a tuple, eg: (3, 6139861153, 'Shufersal', 'Phone Call', '05-28', 'OTHER', 'Follow up')
# row_dict is dict, eg; {'id': 3, 'chat_id': 6139861153, 'subject': 'Shufersal', 'event': 'Phone Call', 'date': '05-28', 'enumerated': 'OTHER', 'more_info': 'Follow up'}
def check_onetime_event(row_dict: dict, conn):
    if row_dict['enumerated'] in ['OTHER', "EVENT"]:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id=?", (row_dict['id'],))
        conn.commit()
        logging.info("Deleted one time event. ")


# QUESTION: we have activated a few cursor in the functions ? can you have a few cursors together ???
def check_monthly_event(row_dict: dict, conn):
    if row_dict['enumerated'] == 'MONTHLY_REMINDER':
        old_date = row_dict['date']
        # make the old date a datetime object
        date_object = datetime.datetime.strptime(old_date, "%m-%d").date().replace(year=datetime.datetime.now().year)
        new_date = date_object.replace(month=date_object.month + 1)
        new_date_string = new_date.strftime("%m-%d")
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET date=? WHERE id=?", (new_date_string, row_dict['id'],))
        conn.commit()
        logging.info("Updated the next date for current monthly event.")


# scan_database([0,3])


def get_user_datas(chat_id):
    conn = safe_db_connection()
    cursor = conn.cursor()
    column_names = get_column_names(cursor)
    cursor.execute("SELECT * from events where chat_id=?", (chat_id,))
    rows = cursor.fetchall()
    rows_list = []
    for row in rows:
        row_dict = {}
        for i, names in enumerate(column_names):
            row_dict[names] = row[i]
        rows_list.append(row_dict)
    return rows_list

# testing
# print(get_user_datas())