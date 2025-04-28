import os
import sqlite3

def add_is_verified_column():
    try:
        # Check if database exists
        db_path = 'app/restaurant.db'
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return
            
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", [table[0] for table in tables])
        
        # Find the user table (case insensitive)
        user_table = None
        for table in tables:
            if table[0].lower() == 'user':
                user_table = table[0]
                break
                
        if not user_table:
            print("User table not found in database")
            return
            
        print(f"Found user table: {user_table}")
        
        # Add column
        try:
            cursor.execute(f"ALTER TABLE {user_table} ADD COLUMN is_verified BOOLEAN DEFAULT 0")
            conn.commit()
            print(f"Successfully added is_verified column to {user_table} table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Column already exists, no changes needed")
            else:
                print(f"Error adding column: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    add_is_verified_column() 