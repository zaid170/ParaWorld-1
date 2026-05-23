from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import datetime
from werkzeug.utils import secure_filename
import google.generativeai as genai

app = Flask(__name__)

# Secure key used to encrypt browser cookies for session tracking
app.secret_key = 'paraworld_cosmic_secure_key_2026'

# --- 📁 DATABASE PATHS ---
SCHOLARSHIP_FILE = 'scholarship_students.json'
ENQUIRY_FILE = 'general_enquiries.json'
SETTINGS_FILE = 'settings.json'
NOTICES_FILE = 'notices.json'
GALLERY_FILE = 'gallery_photos.json'
COMMUNITY_FILE = 'community_posts.json'
FLAGGED_FILE = 'flagged_comments.json'
TOPPERS_FILE = 'toppers.json'

# --- 🖼️ IMAGE UPLOAD SETTINGS ---
UPLOAD_FOLDER = 'static/uploads'
# Create the uploads folder automatically if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- 🤖 PARA GEMINI AI SETUP ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
model = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model = genai.GenerativeModel(model_name=m.name)
                if 'flash' in m.name.lower():
                    break
    except Exception as e:
        print(f"Warning: Could not connect to Google AI: {e}")

# --- ⚡ ANTI-CACHE FORCE RULE ---
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# --- 🛠️ BULLETPROOF DATABASE METHODS ---
def load_data(filepath, default_structure=[]):
    if not os.path.exists(filepath):
        save_data(filepath, default_structure)
        return default_structure
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return default_structure
            return json.loads(content)
    except Exception:
        return default_structure

def load_settings():
    default_ai = (
        "You are Para Gemini, an official AI tutor for Paraworld Educations in Shopian. "
        "You help students solve math problems, answer science questions, and provide info about the institute. "
        "Keep your answers clear, concise, and friendly."
    )
    default_settings = {
        "show_scholarship_junior": True,
        "show_scholarship_senior": True,
        "ai_prompt": default_ai,
        "low_power_mode": False
    }
    return load_data(SETTINGS_FILE, default_settings)

def save_data(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- 🏠 PUBLIC PAGES ---
@app.route('/')
def home():
    settings = load_settings()
    notices = load_data(NOTICES_FILE)
    toppers = load_data(TOPPERS_FILE)
    return render_template(
        'index.html', 
        show_scholarship_junior=settings.get('show_scholarship_junior', True), 
        show_scholarship_senior=settings.get('show_scholarship_senior', True), 
        notices=notices,
        toppers=toppers,
        low_power=settings.get('low_power_mode', False)
    )

@app.route('/gallery')
def gallery():
    photos = load_data(GALLERY_FILE)
    return render_template('gallery.html', photos=photos)

@app.route('/community')
def community():
    posts = load_data(COMMUNITY_FILE)
    return render_template('community.html', posts=posts)

# --- 🔑 ADMINISTRATOR ROUTING ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        try:
            data = request.get_json() or request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password')

            # Cleaned login specifically to admin@paraworld.com
            if email == 'admin@paraworld.com' and password == 'Para World -- @mansa':
                session['logged_in'] = True
                return jsonify({"status": "success", "message": "Access Granted! Welcome back."})
            else:
                return jsonify({"status": "error", "message": "Invalid administrator credentials."}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return render_template('login.html')

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    students = load_data(SCHOLARSHIP_FILE)
    enquiries = load_data(ENQUIRY_FILE)
    settings = load_settings()
    notices = load_data(NOTICES_FILE)
    photos = load_data(GALLERY_FILE)
    posts = load_data(COMMUNITY_FILE)
    toppers = load_data(TOPPERS_FILE)
    flagged = load_data(FLAGGED_FILE)
    
    return render_template(
        'admin.html', 
        students=students, 
        enquiries=enquiries, 
        settings=settings, 
        notices=notices,
        photos=photos,
        posts=posts,
        toppers=toppers,
        flagged=flagged
    )

# --- 🎓 SCHOLARSHIP & GENERAL ENQUIRIES API ---
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    try:
        data = request.get_json()
        enquiries = load_data(ENQUIRY_FILE)
        new_enquiry = {
            "id": len(enquiries) + 1,
            "name": data.get('name'),
            "phone": data.get('phone'),
            "grade": data.get('grade')
        }
        enquiries.append(new_enquiry)
        save_data(ENQUIRY_FILE, enquiries)
        return jsonify({"status": "success", "message": "Enquiry submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register-scholarship', methods=['POST'])
def register_scholarship():
    try:
        data = request.get_json()
        students = load_data(SCHOLARSHIP_FILE)
        new_student = {
            "roll_number": f"PW-2026-{101 + len(students)}",
            "name": data.get('name'),
            "email": data.get('email'),
            "residence": data.get('residence'),
            "phone": data.get('phone'),
            "school": data.get('school'),
            "current_class": data.get('currentClass'),
            "promoting_class": data.get('promotingClass'),
            "heard_from": data.get('heardFrom')
        }
        students.append(new_student)
        save_data(SCHOLARSHIP_FILE, students)
        return jsonify({"status": "success", "message": "Student registered!", "student": new_student}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 💬 ACTIVE COMMUNITY SYSTEM ENDPOINTS ---
@app.route('/api/like-post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    posts = load_data(COMMUNITY_FILE)
    for p in posts:
        if p['id'] == post_id:
            p['likes'] = p.get('likes', 0) + 1
            save_data(COMMUNITY_FILE, posts)
            return jsonify({"status": "success", "likes": p['likes']}), 200
    return jsonify({"status": "error", "message": "Post not found."}), 404

@app.route('/api/comment-post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    data = request.get_json()
    posts = load_data(COMMUNITY_FILE)
    
    new_comment = {
        "id": int(datetime.datetime.now().timestamp() * 1000),
        "author": data.get('author', 'Anonymous'),
        "text": data.get('text', ''),
        "approved": False
    }
    
    for p in posts:
        if p['id'] == post_id:
            if 'comments' not in p:
                p['comments'] = []
            p['comments'].append(new_comment)
            save_data(COMMUNITY_FILE, posts)
            return jsonify({"status": "success", "message": "Awaiting admin approval."}), 200
            
    return jsonify({"status": "error", "message": "Post not found."}), 404

@app.route('/api/flag-comment', methods=['POST'])
def flag_comment():
    data = request.get_json()
    flagged = load_data(FLAGGED_FILE)
    
    new_flag = {
        "id": len(flagged) + 1,
        "author": data.get('author'),
        "text": data.get('text'),
        "post_id": data.get('post_id'),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    flagged.append(new_flag)
    save_data(FLAGGED_FILE, flagged)
    return jsonify({"status": "success"}), 200

# --- 👑 ADMINISTRATIVE MANAGEMENT ACTIONS ---
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    students = load_data(SCHOLARSHIP_FILE)
    
    streams = {}
    classes = {}
    for s in students:
        stream = s.get('promoting_class', 'General')
        cls = s.get('current_class', 'General')
        streams[stream] = streams.get(stream, 0) + 1
        classes[cls] = classes.get(cls, 0) + 1
        
    return jsonify({"status": "success", "streams": streams, "classes": classes}), 200

# UNIFIED SETTINGS UPDATER
@app.route('/update-settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    data = request.get_json()
    settings = load_settings()
    
    for key, value in data.items():
        settings[key] = value
        
    save_data(SETTINGS_FILE, settings)
    return jsonify({"status": "success"}), 200

# Notice Board
@app.route('/add-notice', methods=['POST'])
def add_notice():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    data = request.get_json()
    notices = load_data(NOTICES_FILE)
    new_notice = {
        "id": len(notices) + 1,
        "text": data.get('text')
    }
    notices.append(new_notice)
    save_data(NOTICES_FILE, notices)
    return jsonify({"status": "success"}), 200

@app.route('/delete-notice/<int:notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    notices = [n for n in load_data(NOTICES_FILE) if n['id'] != notice_id]
    save_data(NOTICES_FILE, notices)
    return jsonify({"status": "success"}), 200

# Community Board management
@app.route('/add-post', methods=['POST'])
def add_post():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    data = request.get_json()
    posts = load_data(COMMUNITY_FILE)
    new_post = {
        "id": len(posts) + 1,
        "title": data.get('title'),
        "content": data.get('content'),
        "date": datetime.datetime.now().strftime("%B %d, %Y"),
        "likes": 0,
        "comments": []
    }
    posts.append(new_post)
    save_data(COMMUNITY_FILE, posts)
    return jsonify({"status": "success"}), 200

@app.route('/approve-comment/<int:post_id>/<int:comment_id>', methods=['POST'])
def approve_comment(post_id, comment_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    posts = load_data(COMMUNITY_FILE)
    for p in posts:
        if p['id'] == post_id:
            for c in p.get('comments', []):
                if c['id'] == comment_id:
                    c['approved'] = True
                    save_data(COMMUNITY_FILE, posts)
                    return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

@app.route('/delete-comment/<int:post_id>/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    posts = load_data(COMMUNITY_FILE)
    for p in posts:
        if p['id'] == post_id:
            p['comments'] = [c for c in p.get('comments', []) if c['id'] != comment_id]
            save_data(COMMUNITY_FILE, posts)
            return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

# Flagged comments alerts clearing
@app.route('/clear-flagged', methods=['POST'])
def clear_flagged():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    save_data(FLAGGED_FILE, [])
    return jsonify({"status": "success"}), 200

# Campus Gallery Photo Management (Upgraded for Device Uploads)
@app.route('/add-photo', methods=['POST'])
def add_photo():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    
    file = request.files.get('photo')
    title = request.form.get('title')
    description = request.form.get('description')

    if not file or not title:
        return jsonify({"status": "error", "message": "Missing file or title"}), 400

    # Secure the file and save to static/uploads
    filename = secure_filename(file.filename)
    unique_filename = f"{int(datetime.datetime.now().timestamp())}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    photos = load_data(GALLERY_FILE)
    new_photo = {
        "id": len(photos) + 1,
        "url": f"/{filepath}",  # This generates the perfect URL for the HTML to read
        "title": title,
        "description": description
    }
    photos.append(new_photo)
    save_data(GALLERY_FILE, photos)
    return jsonify({"status": "success"}), 200

@app.route('/delete-photo/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    photos = [p for p in load_data(GALLERY_FILE) if p['id'] != photo_id]
    save_data(GALLERY_FILE, photos)
    return jsonify({"status": "success"}), 200

# Toppers Board management (Upgraded for Device Uploads)
@app.route('/add-topper', methods=['POST'])
def add_topper():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    
    file = request.files.get('photo')
    name = request.form.get('name')
    rank = int(request.form.get('rank', 1))
    score = request.form.get('score')
    quote = request.form.get('quote')
    subject = request.form.get('subject', 'Overall')

    if not file or not name or not score:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Secure the file and save to static/uploads
    filename = secure_filename(file.filename)
    unique_filename = f"topper_{int(datetime.datetime.now().timestamp())}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    toppers = load_data(TOPPERS_FILE)
    new_topper = {
        "id": len(toppers) + 1,
        "name": name,
        "rank": rank,
        "score": score,
        "photo": f"/{filepath}",
        "quote": quote,
        "subject": subject
    }
    toppers.append(new_topper)
    save_data(TOPPERS_FILE, toppers)
    return jsonify({"status": "success"}), 200

@app.route('/delete-topper/<int:topper_id>', methods=['DELETE'])
def delete_topper(topper_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    toppers = [t for t in load_data(TOPPERS_FILE) if t['id'] != topper_id]
    save_data(TOPPERS_FILE, toppers)
    return jsonify({"status": "success"}), 200

# Database Records cleanup
@app.route('/delete-student/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    students = [s for s in load_data(SCHOLARSHIP_FILE) if s['roll_number'] != roll_number]
    save_data(SCHOLARSHIP_FILE, students)
    return jsonify({"status": "success"}), 200

@app.route('/delete-enquiry/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    enquiries = [e for e in load_data(ENQUIRY_FILE) if e['id'] != enquiry_id]
    save_data(ENQUIRY_FILE, enquiries)
    return jsonify({"status": "success"}), 200

@app.route('/update-ai', methods=['POST'])
def update_ai():
    if not session.get('logged_in'): return jsonify({"status": "error"}), 403
    data = request.get_json()
    settings = load_settings()
    settings['ai_prompt'] = data.get('ai_prompt')
    save_data(SETTINGS_FILE, settings)
    return jsonify({"status": "success"}), 200

# --- 🤖 PARA GEMINI AI CHAT ROUTE ---
@app.route('/api/chat', methods=['POST'])
def mini_gemini_chat():
    if not model:
        return jsonify({"status": "error", "message": "Para Gemini is currently starting up or offline."}), 500
        
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"status": "error", "message": "Please type a message!"}), 400
            
        settings = load_settings()
        ai_prompt = settings.get('ai_prompt', "You are Para Gemini, an official AI tutor for Paraworld Educations.")
        
        full_prompt = f"{ai_prompt}\n\nStudent asks: {user_message}"
        response = model.generate_content(full_prompt)
        
        return jsonify({"status": "success", "response": response.text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Google Error Details: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
