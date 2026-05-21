from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os

app = Flask(__name__)

# Secure key used to encrypt browser cookies
app.secret_key = 'paraworld_cosmic_secure_key_2026'

# Local databases
SCHOLARSHIP_FILE = 'scholarship_students.json'
ENQUIRY_FILE = 'general_enquiries.json'

# Authorized Admin Emails (Email-based security system)
AUTHORIZED_EMAILS = ['admin@paraworld.com', 'mansaumer@paraworld.com']
ADMIN_PASSWORD = 'paraworld2026'

# --- HELPER DATABASE METHODS ---
def load_data(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def save_data(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- WEB PAGES AND SERVICES ---

@app.route('/')
def home():
    """Renders the main homepage."""
    return render_template('index.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """
    Renders the custom cosmic login gate.
    Validates verified email and password securely.
    """
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
    """Clears the secure session cookie and locks the admin dashboard."""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin-dashboard')
def admin_dashboard():
    """
    Renders the secure enterprise admin panel.
    If unauthorized, redirects the client to the login page immediately.
    """
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    students = load_data(SCHOLARSHIP_FILE)
    enquiries = load_data(ENQUIRY_FILE)
    
    return render_template('admin.html', students=students, enquiries=enquiries)

# --- CLIENT API ENDPOINTS ---

@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    """
    Saves a general contact enquiry into the database.
    """
    try:
        data = request.get_json()
        student_name = data.get('name')
        student_phone = data.get('phone')
        grade_level = data.get('grade')
        
        if not student_name or not student_phone or not grade_level:
            return jsonify({"status": "error", "message": "Please enter all required fields!"}), 400
            
        enquiries = load_data(ENQUIRY_FILE)
        
        # Structure the enquiry record
        new_enquiry = {
            "id": len(enquiries) + 1,
            "name": student_name,
            "phone": student_phone,
            "grade": grade_level
        }
        
        enquiries.append(new_enquiry)
        save_data(ENQUIRY_FILE, enquiries)
        
        print(f"[LIVE DATABASE ENQUIRY] {student_name} registered for stream: {grade_level}")
        return jsonify({"status": "success", "message": "Enquiry registered successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register-scholarship', methods=['POST'])
def register_scholarship():
    """
    Registers a student for the Scholarship Test, generating a roll number.
    Includes verified student emails, current classes, and promoting classes.
    """
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
            return jsonify({"status": "error", "message": "All fields are required to register!"}), 400

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
            "message": "Registration complete!",
            "student": new_student
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SECURE ADMINISTRATIVE DELETE ENDPOINTS ---

@app.route('/delete-student/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    """Securely deletes a scholarship nominee."""
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized access attempt!"}), 403
        
    try:
        students = load_data(SCHOLARSHIP_FILE)
        updated_students = [s for s in students if s['roll_number'] != roll_number]
        
        if len(students) == len(updated_students):
            return jsonify({"status": "error", "message": "Candidate not found!"}), 404
            
        save_data(SCHOLARSHIP_FILE, updated_students)
        return jsonify({"status": "success", "message": "Candidate removed successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-enquiry/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    """Securely deletes an admission enquiry."""
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized access attempt!"}), 403
        
    try:
        enquiries = load_data(ENQUIRY_FILE)
        updated_enquiries = [e for e in enquiries if e['id'] != enquiry_id]
        
        if len(enquiries) == len(updated_enquiries):
            return jsonify({"status": "error", "message": "Enquiry record not found!"}), 404
            
        save_data(ENQUIRY_FILE, updated_enquiries)
        return jsonify({"status": "success", "message": "Enquiry removed successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
