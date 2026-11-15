import os
import re
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
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

def get_announcements(category='', search='', club=''):
    query = 'SELECT * FROM announcements'
    params = []
    conditions = []

    if category and category.lower() != 'all':
        conditions.append('LOWER(category) = LOWER(?)')
        params.append(category)

    if club:
        clean_club = re.sub(r'[^a-z0-9]', '', club.lower())
        conditions.append('''
            (
                LOWER(club_name) LIKE ? 
                OR LOWER(?) LIKE '%' || LOWER(club_name) || '%'
                OR REPLACE(REPLACE(LOWER(club_name), ' ', ''), '-', '') LIKE ?
                OR ? LIKE '%' || REPLACE(REPLACE(LOWER(club_name), ' ', ''), '-', '') || '%'
            )
        ''')
        params.extend([f'%{club.lower()}%', club.lower(), f'%{clean_club}%', clean_club])

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
        return [dict(row) for row in rows]

def create_announcement(club_name, title, category, content, event_date, link, author_name, is_pinned):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO announcements (club_name, title, category, content, event_date, link, author_name, is_pinned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (club_name, title, category, content, event_date, link, author_name, is_pinned))
        conn.commit()
        new_id = cursor.lastrowid

        cursor.execute('SELECT * FROM announcements WHERE id = ?', (new_id,))
        return dict(cursor.fetchone())

def delete_announcement(announcement_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        conn.commit()
        return cursor.rowcount > 0
