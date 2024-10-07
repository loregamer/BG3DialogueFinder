# web.py - Flask Backend with reverted revision handling and integrated database path

from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)


# Database path handling
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    search_by = request.form['search_by']

    if search_by == 'filename':
        results = query_db('SELECT * FROM filename WHERE filename LIKE ?', [f"%{search_term}%"])
    elif search_by == 'dialogue':
        results = query_db('SELECT * FROM filename WHERE dialogue LIKE ?', [f"%{search_term}%"])
    elif search_by == 'character':
        results = query_db('SELECT * FROM filename WHERE character LIKE ?', [f"%{search_term}%"])

    formatted_results = []
    for result in results:
        file_id = result[0]
        revisions = query_db('SELECT revision FROM revisions WHERE file_id = ?', [file_id])
        formatted_results.append({
            'id': file_id,
            'filename': result[1],
            'dialogue': result[2],
            'character': result[3],
            'type': result[4],
            'revisions': [rev[0] for rev in revisions]
        })

    return jsonify(formatted_results)

@app.route('/submit_revision', methods=['POST'])
def submit_revision():
    file_id = request.form['file_id']
    revision = request.form['revision']
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO revisions (file_id, revision) VALUES (?, ?)", (file_id, revision))
    conn.commit()
    conn.close()
    
    return 'Revision submitted!'

@app.route('/view_revisions')
def view_revisions():
    results = query_db("""
        SELECT f.id, f.filename, f.dialogue, f.character, f.type, r.revision
        FROM filename f
        JOIN revisions r ON f.id = r.file_id
    """)

    formatted_results = []
    current_file_id = None
    current_file_data = None

    for row in results:
        file_id = row[0]
        if file_id != current_file_id:
            if current_file_data:
                formatted_results.append(current_file_data)
            current_file_data = {
                'id': file_id,
                'filename': row[1],
                'dialogue': row[2],
                'character': row[3],
                'type': row[4],
                'revisions': []
            }
            current_file_id = file_id
        
        current_file_data['revisions'].append(row[5])

    if current_file_data:
        formatted_results.append(current_file_data)

    return jsonify(formatted_results)

if __name__ == '__main__':
    app.run(debug=True, port=34611, host='0.0.0.0')