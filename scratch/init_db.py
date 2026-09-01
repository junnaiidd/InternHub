import mysql.connector
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'junnaiidd'
}

def init_db():
    print("Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        print("Please make sure MySQL is running locally on port 3306 and the password 'junnaiidd' is correct.")
        return False

    print("Connected successfully. Reading database.sql...")
    try:
        with open("database.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
    except Exception as e:
        print(f"Error reading database.sql: {e}")
        cursor.close()
        conn.close()
        return False

    # We need to execute the SQL commands.
    # We can split the file by semicolon, but we need to be careful with multi-line statements or comments.
    # A simple parser that splits by semicolon but ignores it inside strings or comments.
    # Since database.sql is simple, we can split by semicolon.
    statements = []
    current_statement = []
    for line in sql_content.splitlines():
        # Remove comments
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('--'):
            continue
        current_statement.append(line)
        if stripped_line.endswith(';'):
            statements.append("\n".join(current_statement))
            current_statement = []

    print(f"Found {len(statements)} SQL statements to execute.")
    
    # Run each statement
    for i, stmt in enumerate(statements):
        stmt_stripped = stmt.strip()
        if not stmt_stripped:
            continue
        try:
            # If it's a USE database command, we handle it or just let it run
            cursor.execute(stmt_stripped)
            print(f"[{i+1}/{len(statements)}] Executed statement successfully.")
        except Exception as e:
            print(f"Error executing statement:\n{stmt_stripped}\nError: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return False

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialization completed successfully!")
    return True

if __name__ == "__main__":
    init_db()
