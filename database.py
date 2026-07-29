import sqlite3

# 1. Connect to the SQLite file
conn = sqlite3.connect("careerlens.db", check_same_thread=False)
cursor = conn.cursor()

# 2. Create the Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        is_verified INTEGER DEFAULT 0,
        verification_code TEXT,
        reset_token TEXT   
    )
''')

# Create the Resume Details table 
cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        phone TEXT,
        resume_email TEXT,
        linkedin_url TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users (email)
    )
''')

# 3. Save the changes to the file
conn.commit()

# We will use this tiny helper function later to talk to the database
def get_db_connection():
    return conn, cursor