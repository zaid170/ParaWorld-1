from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# File name where scholarship student data will be saved
DATA_FILE = 'scholarship_students.json'

def load_registrations():
    """
    Helper function to load student records from the JSON file.
    If the file does not exist yet, it returns an empty list.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading registrations: {e}")
        return []

def save_registrations(data):
    """
    Helper function to save student records back to the JSON file.
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving registrations: {e}")

@app.route('/')
def home():
    """
    Renders the main homepage (index.html).
    """
    return render_template('index.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    """
    Renders the private Admin Portal (admin.html) and passes
    the list of registered students to display in the table.
    """
    students = load_registrations()
    return render_template('admin.html', students=students)

@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    """
    Handles general questions sent from the footer form.
    """
    try:
        data = request.get_json()
        student_name = data.get('name')
        student_phone = data.get('phone')
        grade_level = data.get('grade')
        
        if not student_name or not student_phone or not grade_level:
            return jsonify({"status": "error", "message": "All fields are required!"}), 400
            
        print(f"[NEW ENQUIRY] Name: {student_name} | Phone: {student_phone} | Class: {grade_level}")
        return jsonify({"status": "success", "message": "Enquiry registered successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register-scholarship', methods=['POST'])
def register_scholarship():
    """
    Registers a new student for the Scholarship Test, generates
    a sequential roll number, and saves their details.
    """
    try:
        data = request.get_json()
        name = data.get('name')
        residence = data.get('residence')
        phone = data.get('phone')
        school = data.get('school')
        heard_from = data.get('heardFrom')

        # Check if any field is empty
        if not name or not residence or not phone or not school or not heard_from:
            return jsonify({
                "status": "error", 
                "message": "All fields are required to register!"
            }), 400

        students = load_registrations()
        
        # Automatic roll number generation (starts at PW-2026-101 and increases by 1)
        next_id = 101 + len(students)
        roll_number = f"PW-2026-{next_id}"

        new_student = {
            "roll_number": roll_number,
            "name": name,
            "residence": residence,
            "phone": phone,
            "school": school,
            "heard_from": heard_from
        }

        # Add the new student to our list and save it
        students.append(new_student)
        save_registrations(students)

        # Return success with the student details so the front-end can build the roll slip
        return jsonify({
            "status": "success",
            "message": "Registration complete!",
            "student": new_student
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-student/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    """
    Allows administrators to permanently remove a candidate
    from the scholarship registration file securely.
    """
    try:
        students = load_registrations()
        # Filter out the student with the matching roll number
        updated_students = [s for s in students if s['roll_number'] != roll_number]
        
        if len(students) == len(updated_students):
            return jsonify({"status": "error", "message": "Candidate not found!"}), 404
            
        save_registrations(updated_students)
        print(f"[REMOVED CANDIDATE] Roll Number: {roll_number}")
        return jsonify({"status": "success", "message": "Candidate removed successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run our server application locally on Port 5000
    app.run(debug=True, port=5000)