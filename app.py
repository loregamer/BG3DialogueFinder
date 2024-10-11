import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key needed for session handling

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
            'dialogue': row['dialogue'],
            'character': row['character'],
            'type': row['type']
        })

    conn.close()
    return jsonify(data)

# Save proposed changes to the revisions table (instead of direct update)
@app.route('/update_entry', methods=['POST'])
def update_entry():
    entry_id = request.form['id']
    field = 'dialogue' if 'dialogue' in request.form else 'character'
    new_value = request.form[field]

    # Capture the IP address of the submitter
    submitter_ip = request.remote_addr

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the proposed change into the revisions table, along with the IP and timestamp
    cursor.execute("""
        INSERT INTO revisions (entry_id, field, new_value, submitter_ip)
        VALUES (?, ?, ?, ?)
    """, (entry_id, field, new_value, submitter_ip))

    conn.commit()
    conn.close()

    return "Revision submitted for approval!"

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'forrealgoaway':  # Set your password here
            session['logged_in'] = True
            return redirect(url_for('revisions_page'))
        else:
            flash('Incorrect password, please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

# Display the revisions page for manual approval with authentication
@app.route('/revisions', methods=['GET'])
def revisions_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all pending revisions along with corresponding filenames, IP, and timestamp
    cursor.execute("""
        SELECT r.id, r.entry_id, r.field, r.new_value, r.submitter_ip, r.timestamp, f.filename
        FROM revisions r
        JOIN filename f ON r.entry_id = f.id
    """)
    revisions = cursor.fetchall()

    conn.close()

    return render_template('revisions.html', revisions=revisions)

# Verify and commit changes to the filename table
@app.route('/verify_revision', methods=['POST'])
def verify_revision():
    revision_id = request.form['revision_id']
    entry_id = request.form['entry_id']
    field = request.form['field']
    new_value = request.form['new_value']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the original filename table with the verified change
    cursor.execute(f"""
        UPDATE filename
        SET {field} = ?
        WHERE id = ?
    """, (new_value, entry_id))

    # Remove the revision from the revisions table after it's verified
    cursor.execute("DELETE FROM revisions WHERE id = ?", (revision_id,))

    conn.commit()
    conn.close()

    return "Revision successfully verified and committed!"

# Reject a revision
@app.route('/reject_revision', methods=['POST'])
def reject_revision():
    revision_id = request.form['revision_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Remove the revision from the revisions table
    cursor.execute("DELETE FROM revisions WHERE id = ?", (revision_id,))

    conn.commit()
    conn.close()

    return "Revision successfully rejected!"

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=34611, host='0.0.0.0')