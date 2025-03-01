import os
import sqlite3

def test_db_connection():
    """Test the connection to the database and verify its structure"""
    try:
        # Get the path to the database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the filename table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='filename'")
        if not cursor.fetchone():
            print("ERROR: 'filename' table not found in the database!")
            return False
        
        # Check the structure of the filename table
        cursor.execute("PRAGMA table_info(filename)")
        columns = cursor.fetchall()
        column_names = [col['name'] for col in columns]
        
        required_columns = ['id', 'filename', 'dialogue', 'character', 'type']
        for col in required_columns:
            if col not in column_names:
                print(f"ERROR: Required column '{col}' not found in the 'filename' table!")
                return False
        
        # Count the number of rows in the table
        cursor.execute("SELECT COUNT(*) FROM filename")
        row_count = cursor.fetchone()[0]
        print(f"Database connection successful. Found {row_count} entries in the 'filename' table.")
        
        # Test a simple query
        cursor.execute("SELECT * FROM filename LIMIT 5")
        sample_rows = cursor.fetchall()
        print("\nSample data from the database:")
        for row in sample_rows:
            print(f"ID: {row['id']}, Filename: {row['filename']}, Character: {row['character']}")
        
        conn.close()
        return True
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    success = test_db_connection()
    if success:
        print("\nDatabase test completed successfully!")
    else:
        print("\nDatabase test failed!") 