import os
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key needed for session handling

 #ip_ban_list = ['127.0.0.2']

 #@app.before_request
 #def block_method():
    #ip = request.environ.get('REMOTE_ADDR')
    #if ip in ip_ban_list:
       # abort(403)

# Database path handling
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
    search_term_1 = request.form.get('search_term_1')
    search_by_1 = request.form.get('search_by_1')
    search_term_2 = request.form.get('search_term_2')
    search_by_2 = request.form.get('search_by_2')
    search_term_3 = request.form.get('search_term_3')
    search_by_3 = request.form.get('search_by_3')
    

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
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    data = []
    for row in results:
        data.append({
            'id': row['id'],
            'filename': row['filename'],
            'dialogue': row['dialogue'] if (row['dialogue'] is not None and row['dialogue'].strip() != '') else 'Unknown',
            'character': row['character'] if (row['character'] is not None and row['character'].strip() != '') else 'Unknown',
            'type': row['type'] if (row['type'] is not None and row['type'].strip() != '') else 'Unknown',
        })

    conn.close()
    return jsonify(data)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=34611, host='0.0.0.0')