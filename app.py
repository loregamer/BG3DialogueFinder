import os
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Database path handling
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Serve the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Handle the search request
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    search_by = request.form['search_by']

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM filename WHERE {search_by} LIKE ?"
    cursor.execute(query, ('%' + search_term + '%',))
    results = cursor.fetchall()

    # Prepare results to send back to frontend
    data = []
    for row in results:
        data.append({
            'id': row['id'],
            'filename': row['filename'],
            'dialogue': row['dialogue'],
            'character': row['character'],
            'type': row['type'],
        })

    conn.close()
    return jsonify(data)

# Multi-search functionality
@app.route('/multi_search', methods=['POST'])
def multi_search():
    # Retrieve search terms and filters
    search_term_1 = request.form.get('search_term_1')
    search_by_1 = request.form.get('search_by_1')
    search_term_2 = request.form.get('search_term_2')
    search_by_2 = request.form.get('search_by_2')
    search_term_3 = request.form.get('search_term_3')
    search_by_3 = request.form.get('search_by_3')

    # Build the SQL query dynamically based on non-empty search terms
    conditions = []
    params = []

    if search_term_1:
        conditions.append(f"{search_by_1} LIKE ?")
        params.append(f"%{search_term_1}%")
    
    if search_term_2:
        conditions.append(f"{search_by_2} LIKE ?")
        params.append(f"%{search_term_2}%")
    
    if search_term_3:
        conditions.append(f"{search_by_3} LIKE ?")
        params.append(f"%{search_term_3}%")

    query = "SELECT * FROM filename"
    
    # Add WHERE clause only if there are conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    # Prepare results to send back to frontend
    data = []
    for row in results:
        data.append({
            'id': row['id'],
            'filename': row['filename'],
            'dialogue': row['dialogue'],
            'character': row['character'],
            'type': row['type']
        })

    conn.close()
    return jsonify(data)

# Update database entries
@app.route('/update_entry', methods=['POST'])
def update_entry():
    entry_id = request.form['id']
    field = request.form.get('dialogue') or request.form.get('character')

    # Determine which field to update
    column = 'dialogue' if 'dialogue' in request.form else 'character'

    # Get a connection to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the relevant field in the database
    cursor.execute(f"""
        UPDATE filename
        SET {column} = ?
        WHERE id = ?
    """, (field, entry_id))

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

    return "Entry successfully updated!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=34611, host='0.0.0.0')