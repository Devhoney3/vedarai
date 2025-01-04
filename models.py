import sqlite3

def init_db():
    conn = sqlite3.connect('betting_prediction.db')
    c = conn.cursor()

    # Create Users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    address TEXT NOT NULL,
                    neural_access INTEGER NOT NULL DEFAULT 0,
                    premium_access INTEGER NOT NULL DEFAULT 0,
                    payment_pending INTEGER NOT NULL DEFAULT 0)''')

    # Alter Users table to add neural_access column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN neural_access INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

    # Alter Users table to add premium_access column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN premium_access INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

    # Alter Users table to add payment_pending column if it doesn't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN payment_pending INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

    # Create Predictions table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_name TEXT NOT NULL,
                    match_time TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    odds REAL NOT NULL,
                    result TEXT DEFAULT 'pending',
                    feedback TEXT)''')

    # Alter Predictions table to add premium column if it doesn't exist
    try:
        c.execute("ALTER TABLE predictions ADD COLUMN premium INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

    # Create Stats table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_wins INTEGER NOT NULL,
                    total_losses INTEGER NOT NULL)''')

    # Insert initial stats
    c.execute("INSERT OR IGNORE INTO stats (total_wins, total_losses) VALUES (0, 0)")

    # Create Blogs table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS blogs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT)''')

    # Add an admin user
    c.execute("INSERT OR IGNORE INTO users (username, password, role, address, neural_access, premium_access) VALUES (?, ?, ?, ?, ?, ?)", ('admin', 'admin123', 'admin', 'Admin Address', 1, 1))

    conn.commit()
    conn.close()

