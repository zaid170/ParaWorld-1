from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os

app = Flask(__name__)

# Secure key used to encrypt browser cookies for session tracking
app.secret_key = 'paraworld_cosmic_secure_key_2026'

# Local databases
SCHOLARSHIP_FILE = 'scholarship_students.json'
ENQUIRY_FILE = 'general_enquiries.json'
SETTINGS_FILE = 'settings.json'

# --- YOUR PERSONAL SECURED LOGINS ---
AUTHORIZED_EMAILS = ['zaidbinxubair@gmail.com', 'admin@paraworld.com', 'mansaumer@paraworld.com']
ADMIN_PASSWORD = 'Para World -- @mansa'

# --- BULLETPROOF DATABASE METHODS ---
def load_data(filepath):
    """Safely loads data from a JSON database. If empty, corrupt or missing, heals automatically."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error loading {filepath}, returning empty database: {e}")
        return []

def load_settings():
    """Safely loads global portal settings. Defaults to Scholarship ON."""
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
    """Safely writes structured database lists back to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- WEB PAGES AND SERVICES ---

@app.route('/')
def home():
    """Renders the main landing homepage, checking if Scholarship is ON."""
    settings = load_settings()
    return render_template('index.html', show_scholarship=settings.get('show_scholarship', True))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Renders the secure admin login gateway."""
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        try:
            data = request.get_json() or request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password')

            if email in AUTHORIZED_EMAILS and password == ADMIN_PASSWORD:
                session['logged_in'] = True
                session['user_email'] = email
                session['user_role'] = 'Administrator'
                return jsonify({"status": "success", "message": "Access Granted! Welcome back."})
            else:
                return jsonify({"status": "error", "message": "Invalid administrator email or password."}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return render_template('login.html')

@app.route('/admin-logout')
def admin_logout():
    """Destroys current session tokens and locks the admin environment."""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin-dashboard')
def admin_dashboard():
    """Renders the premium admin control dashboard."""
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    students = load_data(SCHOLARSHIP_FILE)
    enquiries = load_data(ENQUIRY_FILE)
    settings = load_settings()
    
    return render_template('admin.html', students=students, enquiries=enquiries, settings=settings)

# --- CLIENT SUBMISSION API ENDPOINTS ---

@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    """Receives and registers raw program inquiries."""
    try:
        data = request.get_json()
        student_name = data.get('name')
        student_phone = data.get('phone')
        grade_level = data.get('grade')
        
        if not student_name or not student_phone or not grade_level:
            return jsonify({"status": "error", "message": "Please fill out all required fields!"}), 400
            
        enquiries = load_data(ENQUIRY_FILE)
        
        new_enquiry = {
            "id": len(enquiries) + 1,
            "name": student_name,
            "phone": student_phone,
            "grade": grade_level
        }
        
        enquiries.append(new_enquiry)
        save_data(ENQUIRY_FILE, enquiries)
        
        return jsonify({"status": "success", "message": "Enquiry submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register-scholarship', methods=['POST'])
def register_scholarship():
    """Accepts student profiles for the scholarship."""
    settings = load_settings()
    if not settings.get('show_scholarship', True):
        return jsonify({"status": "error", "message": "Scholarship registrations are currently closed."}), 403

    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        residence = data.get('residence')
        phone = data.get('phone')
        school = data.get('school')
        current_class = data.get('currentClass')
        promoting_class = data.get('promotingClass')
        heard_from = data.get('heardFrom')

        if not name or not email or not residence or not phone or not school or not current_class or not promoting_class or not heard_from:
            return jsonify({"status": "error", "message": "All database parameters are mandatory!"}), 400

        students = load_data(SCHOLARSHIP_FILE)
        next_id = 101 + len(students)
        roll_number = f"PW-2026-{next_id}"

        new_student = {
            "roll_number": roll_number,
            "name": name,
            "email": email,
            "residence": residence,
            "phone": phone,
            "school": school,
            "current_class": current_class,
            "promoting_class": promoting_class,
            "heard_from": heard_from
        }

        students.append(new_student)
        save_data(SCHOLARSHIP_FILE, students)

        return jsonify({
            "status": "success",
            "message": "Student registered successfully!",
            "student": new_student
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SECURE ADMINISTRATIVE TOGGLES & ENDPOINTS ---

@app.route('/toggle-scholarship', methods=['POST'])
def toggle_scholarship():
    """Allows Admin to turn the scholarship page ON or OFF."""
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    try:
        data = request.get_json()
        settings = load_settings()
        settings['show_scholarship'] = data.get('show_scholarship', True)
        save_data(SETTINGS_FILE, settings)
        
        return jsonify({"status": "success", "show_scholarship": settings['show_scholarship']}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-student/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Access Denied."}), 403
    try:
        students = load_data(SCHOLARSHIP_FILE)
        updated_students = [s for s in students if s['roll_number'] != roll_number]
        save_data(SCHOLARSHIP_FILE, updated_students)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-enquiry/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Access Denied."}), 403
    try:
        enquiries = load_data(ENQUIRY_FILE)
        updated_enquiries = [e for e in enquiries if e['id'] != enquiry_id]
        save_data(ENQUIRY_FILE, updated_enquiries)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
