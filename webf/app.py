from flask import Flask, request, redirect, url_for, render_template, flash
import mysql.connector
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database configuration
db_config = {
    'user': 'Mreda',
    'password': '123456',
    'host': 'localhost',
    'database': 'n_DB'
}

# Connect to MySQL
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):  # Assuming 'user[2]' is the password column
        return redirect(url_for('explorer_details'))
    else:
        flash("Invalid login credentials")
        return redirect(url_for('index'))

#from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('signup'))

        # Correct hash method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()

        flash("Sign up successful. Please log in.")
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/explorer_details', methods=['GET', 'POST'])
def explorer_details():
    if request.method == 'POST':
        explorer_name = request.form['explorer_name']
        date = request.form['date']
        village = request.form['village']
        center = request.form['center']
        governorate = request.form['governorate']
        guide = request.form['guide']
        guide_phone = request.form['guide_phone']
        guide_id = request.form['guide_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO explorer_details (explorer_name, date, village, center, governorate, guide, guide_phone, guide_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (explorer_name, date, village, center, governorate, guide, guide_phone, guide_id))
        conn.commit()

        # Export to Excel
        cursor.execute("SELECT * FROM explorer_details")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['ID', 'Explorer Name', 'Date', 'Village', 'Center', 'Governorate', 'Guide',
                                         'Guide Phone', 'Guide ID'])
        df.to_excel('C:/Users/muhammed-reda/Documents/admin_details.xlsx', index=False)

        conn.close()
        return redirect(url_for('family_details'))

    return render_template('explorer_details.html')

@app.route('/family_details', methods=['GET', 'POST'])
def family_details():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            return redirect(url_for('add_family_details'))

        elif action == 'save':
            husband_name = request.form['husband_name']
            wife_name = request.form['wife_name']
            husband_national_id = request.form['husband_national_id']
            wife_national_id = request.form['wife_national_id']
            phone = request.form['phone']
            address = request.form['address']
            family_members_count = request.form['family_members_count']
            children_details = request.form['children_details']
            family_income = request.form['family_income']
            husband_job = request.form['husband_job']
            family_health_status = request.form['family_health_status']
            house_condition = request.form['house_condition']
            roof_area = request.form['roof_area']
            distance_to_main_water_pipe = request.form['distance_to_main_water_pipe']
            blankets_count = request.form['blankets_count']
            charity_assistance = request.form['charity_assistance']
            furniture_condition = request.form['furniture_condition']
            clothing_condition = request.form['clothing_condition']
            explorer_opinion = request.form['explorer_opinion']
            acceptance_status = request.form['acceptance_status']
            family_head_id_image = request.files.get('family_head_id_image')

            # Validate input lengths
            if len(husband_national_id) != 14 or len(wife_national_id) != 14:
                flash("Husband and Wife National ID must be 14 digits long")
                return redirect(url_for('family_details'))
            if len(phone) != 11:
                flash("Phone number must be 11 digits long")
                return redirect(url_for('family_details'))

            # Save the image if necessary
            image_path = None
            if family_head_id_image:
                image_path = f'C:/Users/muhammed-reda/Documents/{family_head_id_image.filename}'
                family_head_id_image.save(image_path)

            cursor.execute("""
                INSERT INTO family_details (
                    husband_name, wife_name, husband_national_id, wife_national_id, phone, address, family_members_count,
                    children_details, family_income, husband_job, family_health_status, house_condition, roof_area,
                    distance_to_main_water_pipe, blankets_count, charity_assistance, furniture_condition, clothing_condition,
                    explorer_opinion, family_head_id_image, acceptance_status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                husband_name, wife_name, husband_national_id, wife_national_id, phone, address, family_members_count,
                children_details, family_income, husband_job, family_health_status, house_condition, roof_area,
                distance_to_main_water_pipe, blankets_count, charity_assistance, furniture_condition, clothing_condition,
                explorer_opinion, image_path, acceptance_status
            ))
            conn.commit()

            # Export to Excel
            cursor.execute("SELECT * FROM family_details")
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=[
                'ID', 'Husband Name', 'Wife Name', 'Husband National ID', 'Wife National ID', 'Phone', 'Address',
                'Family Members Count', 'Children Details', 'Family Income', 'Husband Job', 'Family Health Status',
                'House Condition', 'Roof Area', 'Distance to Main Water Pipe', 'Blankets Count', 'Charity Assistance',
                'Furniture Condition', 'Clothing Condition', 'Explorer Opinion', 'Family Head ID Image',
                'Acceptance Status'
            ])
            df.to_excel('C:/Users/muhammed-reda/Documents/needs.xlsx', index=False)
            flash("Family details saved successfully!")

        elif action == 'delete':
            family_id = request.form.get('family_id')
            cursor.execute("DELETE FROM family_details WHERE id = %s", (family_id,))
            conn.commit()
            flash("Family details deleted successfully!")

        elif action == 'edit':
            family_id = request.form.get('family_id')
            return redirect(url_for('edit_family_details', family_id=family_id))

    cursor.execute("SELECT * FROM family_details")
    family_details = cursor.fetchall()
    conn.close()
    return render_template('family_details.html', family_details=family_details)

@app.route('/add_family_details', methods=['GET', 'POST'])
def add_family_details():
    if request.method == 'POST':
        return redirect(url_for('family_details'))

    return render_template('add_family_details.html')

@app.route('/edit_family_details/<int:family_id>', methods=['GET', 'POST'])
def edit_family_details(family_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        husband_name = request.form['husband_name']
        wife_name = request.form['wife_name']
        husband_national_id = request.form['husband_national_id']
        wife_national_id = request.form['wife_national_id']
        phone = request.form['phone']
        address = request.form['address']
        family_members_count = request.form['family_members_count']
        children_details = request.form['children_details']
        family_income = request.form['family_income']
        husband_job = request.form['husband_job']
        family_health_status = request.form['family_health_status']
        house_condition = request.form['house_condition']
        roof_area = request.form['roof_area']
        distance_to_main_water_pipe = request.form['distance_to_main_water_pipe']
        blankets_count = request.form['blankets_count']
        charity_assistance = request.form['charity_assistance']
        furniture_condition = request.form['furniture_condition']
        clothing_condition = request.form['clothing_condition']
        explorer_opinion = request.form['explorer_opinion']
        acceptance_status = request.form['acceptance_status']
        family_head_id_image = request.files.get('family_head_id_image')

        # Validate input lengths
        if len(husband_national_id) != 14 or len(wife_national_id) != 14:
            flash("Husband and Wife National ID must be 14 digits long")
            return redirect(url_for('edit_family_details', family_id=family_id))
        if len(phone) != 11:
            flash("Phone number must be 11 digits long")
            return redirect(url_for('edit_family_details', family_id=family_id))

        # Save the image if necessary
        image_path = None
        if family_head_id_image:
            image_path = f'C:/Users/muhammed-reda/Documents/{family_head_id_image.filename}'
            family_head_id_image.save(image_path)

        cursor.execute("""
            UPDATE family_details
            SET husband_name = %s, wife_name = %s, husband_national_id = %s, wife_national_id = %s, phone = %s, address = %s,
                family_members_count = %s, children_details = %s, family_income = %s, husband_job = %s, family_health_status = %s,
                house_condition = %s, roof_area = %s, distance_to_main_water_pipe = %s, blankets_count = %s, charity_assistance = %s,
                furniture_condition = %s, clothing_condition = %s, explorer_opinion = %s, family_head_id_image = %s, acceptance_status = %s
            WHERE id = %s
        """, (
            husband_name, wife_name, husband_national_id, wife_national_id, phone, address, family_members_count,
            children_details, family_income, husband_job, family_health_status, house_condition, roof_area,
            distance_to_main_water_pipe, blankets_count, charity_assistance, furniture_condition, clothing_condition,
            explorer_opinion, image_path, acceptance_status, family_id
        ))
        conn.commit()

        # Export to Excel
        cursor.execute("SELECT * FROM family_details")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=[
            'ID', 'Husband Name', 'Wife Name', 'Husband National ID', 'Wife National ID', 'Phone', 'Address',
            'Family Members Count', 'Children Details', 'Family Income', 'Husband Job', 'Family Health Status',
            'House Condition', 'Roof Area', 'Distance to Main Water Pipe', 'Blankets Count', 'Charity Assistance',
            'Furniture Condition', 'Clothing Condition', 'Explorer Opinion', 'Family Head ID Image', 'Acceptance Status'
        ])
        df.to_excel('C:/Users/muhammed-reda/Documents/needs.xlsx', index=False)

        flash("Family details updated successfully!")
        conn.close()
        return redirect(url_for('family_details'))

    cursor.execute("SELECT * FROM family_details WHERE id = %s", (family_id,))
    family_detail = cursor.fetchone()
    conn.close()
    return render_template('edit_family_details.html', family_detail=family_detail)

if __name__ == '__main__':
    app.run(debug=True)
