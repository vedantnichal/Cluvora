import os
import json
import re
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from rag import ask

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path=''
)

DB_PATH = os.path.join(BASE_DIR, 'announcements.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_name TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                content TEXT NOT NULL,
                event_date TEXT,
                link TEXT,
                author_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_pinned INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM announcements')
        if cursor.fetchone()[0] == 0:
            seed_data = [
                (
                    "OpenLake",
                    "Open Source Hack Night 2026: Kickoff & Project Pitching",
                    "Sci-Tech",
                    "Join us this Friday for our semester flagship Open Source Hack Night! Pitch your ideas, contribute to campus software projects, and collaborate with peer developers. Snacks and stickers provided!",
                    "Friday, 6:00 PM · CC-3 Lab",
                    "https://github.com/OpenLake",
                    "OpenLake Core Team",
                    1
                ),
                (
                    "Meraz Committee",
                    "Meraz 2026 Techno-Cultural Fest: Volunteer Registrations Live",
                    "Fest",
                    "The flagship techno-cultural festival of IIT Bhilai, Meraz 2026, is calling for enthusiastic student volunteers across Logistics, Sponsorship, Public Relations, and Stage Design.",
                    "Registrations close Nov 25",
                    "https://polaris.iitbhilai.ac.in/views/cosa.php",
                    "CoSA Secretariat",
                    1
                ),
                (
                    "Beat Hackers",
                    "Annual Dance Auditions for Freshers & Sophomores",
                    "Cultural",
                    "Do you have a passion for hip-hop, contemporary, or urban choreography? Beat Hackers invites all dance enthusiasts to our annual auditions. No prior experience required!",
                    "Saturday, 5:30 PM · Student Activity Center",
                    "https://instagram.com/beathackers_iitbhilai",
                    "Dance Club Leads",
                    0
                ),
                (
                    "Spectre",
                    "IIT Bhilai CTF Challenge: Cyber Security Bootcamp",
                    "Sci-Tech",
                    "Ready to test your penetration testing, reverse engineering, and web exploitation skills? Join the Spectre intra-campus CTF. Beginners are highly encouraged to participate!",
                    "Nov 28, 2:00 PM",
                    "https://iitbhilai.ac.in",
                    "Spectre Cyber Sec Club",
                    0
                ),
                (
                    "Sports Council",
                    "Prayatna 2026 Intra-Institute Tournament Schedules Released",
                    "Sports",
                    "The fixtures for Prayatna badminton, football, basketball, and table tennis have been finalized. Check the notice board for team match times and court allocations.",
                    "Tournament Ongoing",
                    "https://polaris.iitbhilai.ac.in",
                    "General Secretary, Sports",
                    0
                )
            ]
            cursor.executemany('''
                INSERT INTO announcements (club_name, title, category, content, event_date, link, author_name, is_pinned)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', seed_data)
        conn.commit()

init_db()

def get_short_description(desc):
    if not desc:
        return ''
    first_sentence = re.split(r'(?<=[.?!])\s+', desc)[0]
    return first_sentence if len(first_sentence) <= 180 else desc[:137] + '...'

def get_cosa_data():
    json_path = os.path.join(BASE_DIR, 'iit_bhilai_cosa_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = get_cosa_data()

@app.route('/')
def home():
    return render_template('Home/index.html', councils=DATA.get('councils', []), clubs=DATA.get('clubs', []))

@app.route('/tech-clubs')
def tech_clubs_page():
    tech = [c for c in DATA.get('clubs', []) if c.get('parent_council') == 'Sci-Tech Council']
    for club in tech:
        club['short_description'] = get_short_description(club.get('description', ''))
    return render_template('Tech Clubs/tech_clubs.html', clubs=tech)

@app.route('/cultural-clubs')
def cultural_clubs_page():
    cult = [c for c in DATA.get('clubs', []) if c.get('parent_council') in ['Cultural Council', 'Media and Publication Body']]
    for club in cult:
        club['short_description'] = get_short_description(club.get('description', ''))
    return render_template('Cultural Clubs/cult_clubs.html', clubs=cult)

@app.route('/societies')
def societies_page():
    soc = [c for c in DATA.get('clubs', []) if 'Society' in c.get('name', '') or 'Society' in c.get('category', '')]
    return render_template('Societies/soc.html', clubs=soc)

@app.route('/announcements')
def announcements_page():
    return render_template('Anouncements/announcements.html')

@app.route('/api/announcements', methods=['GET'])
def get_announcements_api():
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    
    query = 'SELECT * FROM announcements'
    params = []
    conditions = []
    
    if category and category.lower() != 'all':
        conditions.append('LOWER(category) = LOWER(?)')
        params.append(category)
        
    if search:
        conditions.append('(LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(club_name) LIKE ?)')
        wildcard = f'%{search.lower()}%'
        params.extend([wildcard, wildcard, wildcard])
        
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    query += ' ORDER BY is_pinned DESC, id DESC'
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        announcements = [dict(row) for row in rows]
        
    return jsonify({"success": True, "announcements": announcements})

@app.route('/api/announcements', methods=['POST'])
def create_announcement_api():
    data = request.get_json(silent=True) or {}
    club_name = data.get('club_name', '').strip()
    title = data.get('title', '').strip()
    category = data.get('category', 'General').strip()
    content = data.get('content', '').strip()
    event_date = data.get('event_date', '').strip()
    link = data.get('link', '').strip()
    author_name = data.get('author_name', '').strip()
    is_pinned = 1 if data.get('is_pinned') else 0
    
    if not club_name or not title or not content:
        return jsonify({
            "success": False,
            "error": "Club name, title, and announcement details are required."
        }), 400
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO announcements (club_name, title, category, content, event_date, link, author_name, is_pinned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (club_name, title, category, content, event_date, link, author_name, is_pinned))
        conn.commit()
        new_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM announcements WHERE id = ?', (new_id,))
        created = dict(cursor.fetchone())
        
    return jsonify({
        "success": True,
        "message": "Announcement published successfully!",
        "announcement": created
    }), 201

@app.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement_api(announcement_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Announcement not found."}), 404
            
    return jsonify({"success": True, "message": "Announcement deleted successfully."})

@app.route('/contact')
def contact_page():
    return render_template('Contact Us/contact_us.html')

@app.route('/club/<club_id>/details')
def get_club_details(club_id):
    club = next((c for c in DATA.get('clubs', []) if c.get('club_id') == club_id), None)
    if not club:
        return "<p class='loading-state'>Club details not found.</p>", 404
    partial_path = os.path.join(BASE_DIR, 'Tech Clubs', 'club_details_partial.html')
    if os.path.exists(partial_path):
        return render_template('Tech Clubs/club_details_partial.html', club=club)
    return jsonify(club)

@app.route('/chatbot')
def chatbot_page():
    return render_template('Chatbot/chatbot.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    req_data = request.get_json(silent=True) or {}
    message = req_data.get('message', '').strip()
    if not message:
        return jsonify({"reply": "Please enter a question about the IIT Bhilai brochure.", "sources": []})
    
    result = ask(message, top_k=3)
    return jsonify({
        "reply": result["answer"],
        "sources": result["sources"]
    })

if __name__ == '__main__':
    app.run(debug=True)