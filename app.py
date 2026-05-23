from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import google.generativeai as genai

app = Flask(__name__)

# Secure key used to encrypt browser cookies for session tracking
app.secret_key = 'paraworld_cosmic_secure_key_2026'

# Local databases
SCHOLARSHIP_FILE = 'scholarship_students.json'
ENQUIRY_FILE = 'general_enquiries.json'
SETTINGS_FILE = 'settings.json'

# --- MINI GEMINI AI SETUP ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Give Mini Gemini its personality and rules
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are Mini Gemini, an official AI tutor for Paraworld Educations in Shopian. You help students solve math problems, answer science questions, and provide info about the institute. Keep your answers clear, concise, and friendly. Never mention you are made by Google; you are exclusively Mini Gemini for Paraworld."
    )
else:
    model = None

# --- ANTI-CACHE FORCE RULE ---
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# --- BULLETPROOF DATABASE METHODS ---
def load_data(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        return []

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"show_scholarship": True}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return {"show_scholarship": True}
            return json.loads(content)
    except Exception:
        return {"show_scholarship": True}

def save_data(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- WEB PAGES AND SERVICES ---

@app.route('/')
def home():
    settings = load_settings()
    return render_template('index.html', show_scholarship=settings.get('show_scholarship', True))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        try:
            data = request.get_json() or request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password')

            if email in ['zaidbinxubair@gmail.com', 'admin@paraworld.com', 'mansaumer@paraworld.com'] and password == 'Para World -- @mansa':
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
    
    return render_template('admin.html', students=students, enquiries=enquiries, settings=settings)

# --- CLIENT SUBMISSION API ENDPOINTS ---

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
    settings = load_settings()
    if not settings.get('show_scholarship', True):
        return jsonify({"status": "error", "message": "Registrations closed."}), 403

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

# --- SECURE ADMINISTRATIVE TOGGLES ---

@app.route('/toggle-scholarship', methods=['POST'])
def toggle_scholarship():
    if not session.get('logged_in'):
        return jsonify({"status": "error"}), 403
    try:
        data = request.get_json()
        settings = load_settings()
        settings['show_scholarship'] = data.get('show_scholarship', True)
        save_data(SETTINGS_FILE, settings)
        return jsonify({"status": "success", "show_scholarship": settings['show_scholarship']}), 200
    except Exception as e:
        return jsonify({"status": "error"}), 500

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

# --- MINI GEMINI CHAT ENDPOINT ---
@app.route('/api/chat', methods=['POST'])
def mini_gemini_chat():
    """Handles messages between the website and Mini Gemini."""
    if not model:
        return jsonify({"status": "error", "message": "Mini Gemini is currently offline. Missing API Key."}), 500
        
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"status": "error", "message": "Please ask a question!"}), 400
            
        # Ask Google's servers
        response = model.generate_content(user_message)
        
        return jsonify({"status": "success", "response": response.text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Mini Gemini is thinking too hard right now. Try again later!"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
