from flask import Flask, request, jsonify, session
from werkzeug.utils import secure_filename

import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'f174273edf1a9d73552086e19194e92665a0f2c8d5f849f6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/ecommerce.db'

app.config['UPLOADED_IMAGES_DEST'] = 'uploads'  

# SQLite database
def connect_db():
    return sqlite3.connect('ecommerce.db')

@app.route('/', methods=['GET'])
def hello():
        return "Hello"

# Login route
@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return jsonify(message='Already logged in'), 200

    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify(message='Invalid input'), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        session['username'] = username
        session['role'] = user[1]
        session['user_id'] = user[0]  
        print(f'Logged in successfully as {user[1]}. User ID: {user[0]}')
        return jsonify(message=f'Logged in successfully as {user[1]}'), 200
    else:
        return jsonify(message='Invalid credentials'), 401

# Logout
@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('role', None)
        session.pop('user_id', None)  
        return jsonify(message='Logged out successfully'), 200
    else:
        return jsonify(message='Not logged in'), 401

# Upload product for Shopper with image
@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'username' not in session:
        return jsonify(message='Not logged in'), 401

    if session['role'] != 'Shopper':
        return jsonify(message='Unauthorized'), 403

    product_name = request.form.get('product_name')
    price = request.form.get('price')
    uploaded_image = request.files.get('image')

    if not product_name or not price or not uploaded_image:
        return jsonify(message='Invalid input'), 400

    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if '.' not in uploaded_image.filename or \
            uploaded_image.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify(message='Invalid image format. Allowed formats: jpg, jpeg, png'), 400

    shopper_id = session['user_id']

    conn = connect_db()
    cursor = conn.cursor()

    # Save the uploaded image
    image_filename = secure_filename(uploaded_image.filename)
    image_path = os.path.join('uploads', image_filename)
    uploaded_image.save(image_path)

    cursor.execute(
        'INSERT INTO products (product_name, price, image_path, shopper_id) VALUES (?, ?, ?, ?)',
        (product_name, price, image_path, shopper_id))
    conn.commit()
    conn.close()

    return jsonify(message='Product uploaded successfully'), 200

@app.route('/products', methods=['GET'])
def view_products():
    if 'username' not in session or session['role'] != 'Client':
        return jsonify(message='Unauthorized'), 403

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, product_name, price, image_path FROM products')  
    products = cursor.fetchall()

    conn.close()

    product_list = []
    for product in products:
        product_dict = {
            'id': product[0],
            'product_name': product[1],
            'price': product[2],
            'image_path': product[3]  
        }
        product_list.append(product_dict)

    return jsonify(products=product_list), 200

if __name__ == '__main__':
    app.run(debug=True, port=8001)
