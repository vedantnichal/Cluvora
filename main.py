import os
import json
import re
from flask import Flask, render_template, request, jsonify
from rag import ask

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path=''
)

def get_short_description(desc):
    if not desc:
        return ''
    first_sentence = re.split(r'(?<=[.?!])\s+', desc)[0]
    return first_sentence if len(first_sentence) <= 180 else desc[:137] + '...'

def get_cosa_data():
    json_path = os.path.join(FRONTEND_DIR, 'iit_bhilai_cosa_data.json')
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

@app.route('/contact')
def contact_page():
    return render_template('Contact Us/contact_us.html')

@app.route('/club/<club_id>/details')
def get_club_details(club_id):
    club = next((c for c in DATA.get('clubs', []) if c.get('club_id') == club_id), None)
    if not club:
        return "<p class='loading-state'>Club details not found.</p>", 404
    return render_template('Tech Clubs/club_details_partial.html', club=club)

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