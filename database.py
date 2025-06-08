# database.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()

    # Create students table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    submitted INTEGER,
                    score INTEGER,
                    submit_time TEXT,
                    semester TEXT
                )''')

    # Check if questions table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
    if c.fetchone() is None:
        # Table doesn't exist, create it with correct schema
        c.execute('''CREATE TABLE questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT,
                        opt1 TEXT,
                        opt2 TEXT,
                        opt3 TEXT,
                        opt4 TEXT,
                        answer TEXT,
                        semester TEXT
                    )''')
    else:
        # Table exists - check columns
        c.execute("PRAGMA table_info(questions)")
        columns = [col[1] for col in c.fetchall()]
        required_columns = {'id', 'question', 'opt1', 'opt2', 'opt3', 'opt4', 'answer', 'semester'}
        if not required_columns.issubset(set(columns)):
            # Need to migrate table to new schema
            print("Migrating questions table to add missing columns...")
            # Rename old table
            c.execute("ALTER TABLE questions RENAME TO questions_old")

            # Create new table
            c.execute('''CREATE TABLE questions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            opt1 TEXT,
                            opt2 TEXT,
                            opt3 TEXT,
                            opt4 TEXT,
                            answer TEXT,
                            semester TEXT
                        )''')

            # Copy data for columns that exist in old table (best effort)
            existing_columns = set(columns)
            common_columns = existing_columns.intersection(required_columns)
            common_columns.discard('id')  # id is autoincrement

            common_columns_str = ", ".join(common_columns)
            c.execute(f"INSERT INTO questions ({common_columns_str}) SELECT {common_columns_str} FROM questions_old")

            # Drop old table
            c.execute("DROP TABLE questions_old")

    conn.commit()
    conn.close()

def register_student(id, name, semester):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (id, name, submitted, score, submit_time, semester) VALUES (?, ?, 0, 0, '', ?)", (id, name, semester))
    conn.commit()
    conn.close()

def student_exists(sid):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id = ?", (sid,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def verify_student(id, name):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("SELECT submitted, semester FROM students WHERE id = ? AND name = ?", (id, name))
    result = c.fetchone()
    conn.close()
    return result

def submit_exam(id, score):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE students SET submitted = 1, score = ?, submit_time = ? WHERE id = ?", (score, time_str, id))
    conn.commit()
    conn.close()

def get_all_students():
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()
    return data

def delete_student(id):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def reset_student(id):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("UPDATE students SET submitted = 0, score = 0, submit_time = '' WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def add_question(question, o1, o2, o3, o4, answer, semester):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("INSERT INTO questions (question, opt1, opt2, opt3, opt4, answer, semester) VALUES (?, ?, ?, ?, ?, ?, ?)", (question, o1, o2, o3, o4, answer, semester))
    conn.commit()
    conn.close()

def delete_question(qid):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE id = ?", (qid,))
    conn.commit()
    conn.close()

def get_all_questions():
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM questions")
    questions = c.fetchall()
    conn.close()
    return questions

def get_all_questions_by_semester(semester):
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE semester = ?", (semester,))
    questions = c.fetchall()
    conn.close()
    return questions
