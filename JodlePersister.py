import sqlite3

# This seems a bit unclean, maybe it can be done better

# Create table if not exists?
def create_db():
    db = sqlite3.connect("jodel.db")
    cursor = db.cursor()
    cursor.execute(
        '''CREATE TABLE jodel(access_token text, refresh_token text, distinct_id text, device_id text, 
        expiration_date integer)''')
    db.commit()
    db.close()


def add_jodel_account(access_token: str, refresh_token: str, distinct_id: str, device_id: str, expiration_date: int):
    db = sqlite3.connect("jodel.db")
    cursor = db.cursor()
    cursor.execute('''INSERT INTO jodel VALUES (?,?,?,?,?)''',
                   (access_token, refresh_token, distinct_id, device_id, expiration_date))
    db.commit()
    db.close()


def load_jodel_account(count: int) -> list:
    db = sqlite3.connect("jodel.db")
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM jodel LIMIT (?)''', (count,))
    account_list = cursor.fetchall()
    db.close()

    return account_list
