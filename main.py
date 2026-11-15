import os
import json
import re
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from rag import ask
from auth import coordinator_auth, init_auth_db, verify_passcode
from database import init_db, get_announcements, create_announcement, delete_announcement

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path=''
)
app.register_blueprint(coordinator_auth)

init_db()
init_auth_db()

def get_short_description(desc):
    if not desc:
        return ''
    first_sentence = re.split(r'(?<=[.?!])\s+', desc)[0]
    return first_sentence if len(first_sentence) <= 180 else desc[:137] + '...'

def get_cosa_data():
    json_path = os.path.join(BASE_DIR, 'static', 'iit_bhilai_cosa_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = get_cosa_data()

@app.route('/')
def home():
    return render_template('template/index.html', councils=DATA.get('councils', []), clubs=DATA.get('clubs', []))

@app.route('/tech-clubs')
def tech_clubs_page():
    tech = [c for c in DATA.get('clubs', []) if c.get('parent_council') == 'Sci-Tech Council']
    for club in tech:
        club['short_description'] = get_short_description(club.get('description', ''))
    return render_template('template/tech_clubs.html', clubs=tech)

@app.route('/cultural-clubs')
def cultural_clubs_page():
    cult = [c for c in DATA.get('clubs', []) if c.get('parent_council') in ['Cultural Council', 'Media and Publication Body']]
    for club in cult:
        club['short_description'] = get_short_description(club.get('description', ''))
    return render_template('template/cult_clubs.html', clubs=cult)

@app.route('/societies')
def societies_page():
    soc = [c for c in DATA.get('clubs', []) if c.get('parent_council') in ['Student Welfare and Governance', 'Sports Council'] or c.get('category') in ['Welfare & Governance', 'Sports']]
    for club in soc:
        club['short_description'] = get_short_description(club.get('description', ''))
    return render_template('template/soc.html', clubs=soc)

@app.route('/announcements', methods=['GET'])
def announcements_page():
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json' or request.args.get('category') or request.args.get('club') or request.args.get('search'):
        return get_announcements_api()
    return render_template('template/announcements.html')

def get_announcements_api():
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    club = request.args.get('club', '').strip()
    
    announcements = get_announcements(category=category, search=search, club=club)
    return jsonify({"success": True, "announcements": announcements})

@app.route('/announcements', methods=['POST'])
def create_announcement_api():
    post_data = request.get_json(silent=True) or {}
    club_name = post_data.get('club_name', '').strip()
    title = post_data.get('title', '').strip()
    category = post_data.get('category', 'General').strip()
    content = post_data.get('content', '').strip()
    event_date = post_data.get('event_date', '').strip()
    link = post_data.get('link', '').strip()
    author_name = post_data.get('author_name', '').strip()
    is_pinned = 1 if post_data.get('is_pinned') else 0
    
    if not club_name or not title or not content or not author_name:
        return jsonify({
            "success": False,
            "error": "Club name, title, announcement details, and author/role are required."
        }), 400

    passcode = post_data.get('passcode', '').strip()
    if passcode and not verify_passcode(club_name, passcode):
        return jsonify({
            "success": False,
            "error": f"Invalid coordinator passcode for {club_name}."
        }), 403
        
    created = create_announcement(
        club_name=club_name,
        title=title,
        category=category,
        content=content,
        event_date=event_date,
        link=link,
        author_name=author_name,
        is_pinned=is_pinned
    )
        
    return jsonify({
        "success": True,
        "message": "Announcement published successfully!",
        "announcement": created
    }), 201

@app.route('/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement_api(announcement_id):
    if not delete_announcement(announcement_id):
        return jsonify({"success": False, "error": "Announcement not found."}), 404
    return jsonify({"success": True, "message": "Announcement deleted successfully."})

@app.route('/contact')
def contact_page():
    return render_template('template/contact_us.html')

@app.route('/club/<club_id>/details')
def get_club_details(club_id):
    club = next((c for c in DATA.get('clubs', []) if c.get('club_id') == club_id), None)
    if not club:
        return "<p class='loading-state'>Club details not found.</p>", 404
    partial_path = os.path.join(BASE_DIR, 'template', 'club_details_partial.html')
    if os.path.exists(partial_path):
        return render_template('template/club_details_partial.html', club=club)
    return jsonify(club)

@app.route('/chatbot')
def chatbot_page():
    return render_template('template/chatbot.html')

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