import sqlite3
import bcrypt
def get_connection():
    connection = sqlite3.connect('resume_analyzer.db', check_same_thread=False)
    return connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL , 
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
        )''')

    connection.commit()
    connection.close()

def hash_password(password):
    scrambled = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return scrambled.decode('utf-8')
    
def verify_password(password, scrambled_hash):
    return bcrypt.checkpw(password.encode('utf-8'), scrambled_hash.encode('utf-8'))

def add_user(username , password , role="applicant"):
    connection= get_connection()
    cursor =connection.cursor()

    try:
        hashed_pw = hash_password(password)
        cursor.execute('INSERT INTO users(username , password_hash, role) VALUES (? , ? , ?)', (username ,hashed_pw, role))
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()

def authentication_user(username , password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT password_hash, role FROM users WHERE username=? ", (username,))
    
    user_record = cursor.fetchone()
    connection.close()

    if user_record :
        stored_hash = user_record[0]
        role = user_record[1]
        if verify_password(password , stored_hash):
            return role
    return None

    
