import sqlite3


def open_db():
    try:
        dataBase = sqlite3.connect('DataBase/DataBase.db')
        return dataBase
    except sqlite3.Error as error:
        print("error")


def create_db():
    db = open_db()
    cursor = db.cursor()
    create_table = """
    CREATE TABLE IF NOT EXISTS userspass(
        name TEXT PRIMARY KEY,
        hash TEXT NOT NULL,
        salt TEXT
        )
    """
    cursor.execute(create_table)
    db.commit
    db.close()


def get_data(name):
    db = open_db()
    cursor = db.cursor()

    cursor.execute("SELECT hash, salt FROM userspass WHERE name = ?", (name,))
    row = cursor.fetchone()
    db.close()
    
    if not row:
        return None, None
    
    hashed = row[0]
    salt = row[1]

    return hashed, salt


def stor_data(name, hash, salt):
    db = open_db()
    cursor = db.cursor()

    cursor.execute("INSERT OR REPLACE INTO userspass (name, hash, salt) VALUES (?, ?, ?)", (name, hash, salt))
    db.commit()
    db.close()

