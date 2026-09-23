import sqlite3
conn = sqlite3.connect("nutrition.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS foods(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    food_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    calories REAL NOT NULL,
    protein REAL NOT NULL,
    carbs REAL NOT NULL,
    fat REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# ---------------- USER GOALS TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT UNIQUE,
    goal TEXT,
    age INTEGER,
    gender TEXT,
    height REAL,
    current_weight REAL,
    target_weight REAL,
    activity_level TEXT,
    bmi REAL,
    bmr REAL,
    tdee REAL,
    target_calories REAL,
    protein_goal REAL,
    water_goal REAL
)
""")

# Check if created_at already exists in foods table
cursor.execute("PRAGMA table_info(foods)")
columns = [column[1] for column in cursor.fetchall()]

if "created_at" not in columns:
    cursor.execute("""
        ALTER TABLE foods
        ADD COLUMN created_at TIMESTAMP
    """)
cursor.execute("""
    UPDATE foods
    SET created_at = CURRENT_TIMESTAMP
    WHERE created_at IS NULL
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully!")