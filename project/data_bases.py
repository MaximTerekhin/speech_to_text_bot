import sqlite3
from config import BASE_NAME

def execute_quere(sql_quere, data=None, db_path=BASE_NAME):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        if data:
            cursor.execute(sql_quere, data)
        else:
            cursor.execute(sql_quere)
        connection.commit()

def execute_selectoin_quere(sql_quere, data=None, db_path=BASE_NAME):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_quere, data)
    else:
        cursor.execute(sql_quere)
    rows = cursor.fetchall()
    connection.close()
    return rows

def create_table(table_name):
    sql_quere = f'''CREATE TABLE IF NOT EXISTS {table_name}(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    text_gpt TEXT,
    tokens_text INTEGER,
    stt_blocks INTEGER);'''
    execute_quere(sql_quere)

def insert_info(values):
    sql_quere = '''INSERT INTO Users(user_id, text_gpt, tokens_text, stt_blocks) VALUES(?,?,?,?)'''
    execute_quere(sql_quere, values)

def get_blocks(user_id):
    sql_quere = f'''SELECT SUM (stt_blocks) from Users WHERE user_id={user_id}'''
    data = execute_selectoin_quere(sql_quere)
    if data and data[0]:
        return data[0]
    else:
        return





