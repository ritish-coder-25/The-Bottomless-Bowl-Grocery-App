from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, unset_jwt_cookies, jwt_required
from application.models import *
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Api
from application.api import CategoryAPI, ProductAPI, PurchaseAPI #UserCartsAPI
from application.cache import cache
from application.utils import send_email, send_email_monthly

from jinja2 import Environment, FileSystemLoader
import pdfkit
import schedule
import threading
import csv
from sqlalchemy import func
from flask_cors import CORS
from application.utils import send_email
from celery import Celery
from io import BytesIO
import tempfile

app = Flask(__name__, template_folder="templates")

if os.getenv('ENV', "development") == "production":
    raise Exception("Currently no production config is set.")
else:
    print("Starting Local Development")
    app.config.from_object(LocalDevelopmentConfig)

cache.init_app(app, config={'CACHE_TYPE': 'simple'})

db.init_app(app)
JWTManager(app)
CORS(app, supports_credentials=True)
api = Api(app)
app.app_context().push()

api.add_resource(CategoryAPI, '/api/categories', '/api/categories/<int:category_id>')
api.add_resource(ProductAPI, '/api/products', '/api/products/<int:product_id>')
api.add_resource(PurchaseAPI, '/api/purchase')
#api.add_resource(UserCartsAPI, '/api/user-carts')

cache.cached(timeout=600, key_prefix='categories')(CategoryAPI)
cache.cached(timeout=600, key_prefix='products')(ProductAPI)

celery = Celery(
    'app',
    broker='redis://localhost:6379/0',
    backend='rpc://',
)

celery.config_from_object('celeryconfig')

@app.before_first_request
def initialize_database():
    with app.app_context():
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()
        print(table_names)

        if not table_names:
            db.create_all()
            admin = Role(name = 'ADMIN', description = '')
            store_manager = Role(name = 'STORE MANAGER',description = '')
            user = Role(name = 'USER', description = '')

            db.session.add(admin)
            db.session.add(store_manager)
            db.session.add(user)
            db.session.commit()

            print('Database tables created')
        else:
            print('Database Tables already exist')


@app.route('/main.js')
def serve_js():
    return send_from_directory(app.root_path, 'main.js')

# -----------------------------------------------DEFINING THE APP AND API ROUTES--------------------------------------------------------------

@app.route('/validate_admin', methods=['POST'])
def validate_admin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'invalid': False}), 200

    admin = User.query.filter_by(email=email, role='ADMIN').first()

    if admin and check_password_hash(admin.password, password):
        return jsonify({'valid': True}), 200

    return jsonify({'invalid': False}), 200

# ----------------------------------------------------------REGISTERING AND LOGIN-------------------------------------------------------------------------------------------------------
def add_admin():
    email = '21f3000959@ds.study.iitm.ac.in'
    password = 'gaWHkzjp'

    if email and password:
        if User.query.filter_by(email = email).first():
            return {"message": "Admin Already Exists"}, 409

        admin = User(
            email = email,
            password = generate_password_hash(password),
            active = True,
            role = 'ADMIN'
        )
        db.session.add(admin)
        db.session.commit()

        msg = 'Admin registered Successfully'
        print(msg)
    else:
        print("Something went wrong")


@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    msg = ''
    if request.method == 'POST':
    
        email = request.form['email']
        password = request.form['password']

        if email and password:
                if User.query.filter_by(email = email).first():
                    return {"message": "User already exists"}, 409

                user = User(
                    email = email,
                    password = generate_password_hash(password),
                    active = True,
                    role = 'USER'
                )
                db.session.add(user)
                db.session.commit()

                msg = 'User Registered Successfully'
                return redirect(url_for('user_login'))
        else:
            msg = "Missing Details"
            return render_template('user_register.html', msg=msg)
    else:
        return render_template('user_register.html', msg=msg)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    msg=""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.query.filter_by(email=email, role='ADMIN').first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                identity = {'id': user.id, 'email': user.email}
                access_token = create_access_token(identity=identity, expires_delta=timedelta(2))
                response = make_response(jsonify({'message': 'Admin logged in successfully', 'access_token': access_token}))
                response.headers['Access-Control-Allow-Origin'] = "*"
                return response
            else:
                msg = "Wrong Email or Password"
                return jsonify(error=msg), 401
        else:
            msg = "Admin doesn't exist"
            return jsonify(error=msg), 401
    else:
        return render_template('admin_login.html', msg=msg)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    msg=""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.query.filter_by(email=email, role='USER').first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                identity = {'id': user.id, 'email': user.email}
                access_token = create_access_token(identity=identity, expires_delta=timedelta(2))
                response = make_response(jsonify({'message': 'User logged in successfully', 'access_token': access_token}))
                response.headers['Acess-Control-Allow-Origin'] = "*"
                return response
            else:
                msg = "Wrong Email or Password"
                return jsonify(error=msg), 401
        else:
            msg = "User doesn't exist"
            return jsonify(error=msg)
    else:
        return render_template('user_login.html', msg=msg)


@app.route('/store_manager/register_request', methods=['GET', 'POST'])
def store_manager_register_request():
    if request.method == 'POST':
        # Get user details from the request
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email and password:
            if(User.query.filter_by(email=email).first()):
                return jsonify({'message': 'User Already Exists'}), 409

            user_request = UserRequest(email=email, password=password)
            db.session.add(user_request)
            db.session.commit()

            # Notify the admin (you may want to use a message queue or another mechanism for real-world applications)

            return jsonify({'message': 'Registration request sent successfully'}), 200
    else:
        return render_template('store_manager_register.html')

@app.route('/admin/registration_requests')
def registration_requests():
    try:
        # Fetch and return store manager registration requests
        # (you may want to paginate the requests in a real-world scenario)
        # For example:
        requests = UserRequest.query.all()
        return jsonify({'requests': [{'email': req.email, 'password': req.password} for req in requests]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/registration_requests/<string:email>/<string:action>', methods=['POST'])
def process_registration_request(email, action):
    try:
        # Process the registration request (accept or reject)
        # Update the database or perform any necessary actions
        # For example:
        if action == 'accept':
            # Create a new store manager user in the database
            user_request = UserRequest.query.filter_by(email=email).first()
            new_store_manager = User(
                                    email=user_request.email,
                                    password=generate_password_hash(user_request.password),
                                    active=True,
                                    role='STORE MANAGER'
                                )
            db.session.add(new_store_manager)
            db.session.delete(user_request)
            db.session.commit()
        elif action == 'reject':
            # Delete the user request from the database
            user_request = UserRequest.query.filter_by(email=email).first()
            db.session.delete(user_request)
            db.session.commit()

        # For now, returning a dummy response
        return jsonify({'message': 'Request processed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/store_manager/login', methods=['GET', 'POST'])
def store_manager_login():
    msg=""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.query.filter_by(email=email, role='STORE MANAGER').first()
            print("User:", user)

            if user and user.role == 'STORE MANAGER' and check_password_hash(user.password, password):
                print("User Role:", user.role)
                session['user_id'] = user.id
                identity = {'id': user.id, 'email': user.email}
                access_token = create_access_token(identity=identity, expires_delta=timedelta(2))
                response = make_response(jsonify({'message': 'Store Manager logged in successfully', 'access_token': access_token}))
                response.headers['Access-Control-Allow-Origin'] = "*"
                return response
            else:
                msg = "Wrong Email or Password"
                return jsonify(error=msg), 401
        else:
            msg = "User doesn't exist"
            return jsonify(error=msg), 401
    else:
        return render_template('store_manager_login.html', msg=msg)

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/manager/dashboard')
def manager_dashboard():
    return render_template('manager_dashboard.html')

@app.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/admin/logout', methods=['GET', 'POST'])
@jwt_required()
def admin_logout():
    access_token = create_access_token(identity=get_jwt_identity(), expires_delta=timedelta(seconds=1))
    response = make_response(jsonify({'message': 'Admin logged out successfully'}))

    unset_jwt_cookies(response)

    return response

@app.route('/store_manager/logout', methods=['GET', 'POST'])
@jwt_required()
def store_manager_logout():
    access_token = create_access_token(identity=get_jwt_identity(), expires_delta=timedelta(seconds=1))
    response = make_response(jsonify({'message': 'Store Manager logged out successfully'}))

    unset_jwt_cookies(response)

    return response

@app.route('/user/logout', methods=['GET', 'POST'])
@jwt_required()
def user_logout():
    access_token = create_access_token(identity=get_jwt_identity(), expires_delta=timedelta(seconds=1))
    response = make_response(jsonify({'message': 'User logged out successfully'}))

    unset_jwt_cookies(response)

    return response


# ------------------------------------------------------CATEGORIES PART--------------------------------------------------------------------

@app.route('/admin/manage_categories')
def manage_categories():
    return render_template('manage_categories.html')
    #return send_from_directory('MAD-2 Project/templates/', 'manage_categories.html')

@app.route('/manager/requests')
def request_sender():
    user_id = session['user_id']
    return render_template('request_sender.html', user_id=user_id)

@app.route('/admin/requests')
def request_viewer():
    return render_template('request_viewer.html')

@app.route('/app/send-request', methods=['POST'])
def send_request():
    user_id = session['user_id']
    request_text = request.json.get('request_text')

    new_request = Request(user_id=user_id, request_text=request_text, status=None)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'status': 'Request sent successfully'}), 200

@app.route('/app/fetch-requests', methods=['GET'])
def fetch_requests():
    requests = Request.query.all()
    serialized_requests = [{'id': request.id, 'user_id': request.user_id, 'request_text': request.request_text, 'status': request.status} for request in requests]
    return jsonify(serialized_requests), 200

@app.route('/app/update-request-status/<int:request_id>/<status>', methods=['POST'])
def update_request_status(request_id, status):
    request_to_update = Request.query.get(request_id)
    if request_to_update:
        request_to_update.status = status
        db.session.commit()
        return jsonify({ 'status': 'Request status updated successfully' }), 200
    else:
        return jsonify({ 'status': 'Request not found' }), 404

# Route for viewing categories
@app.route('/view_categories')
def view_categories():
    return render_template('view_categories.html')

# ----------------------------------------------------PRODUCTS PART -------------------------------------------------------------------------
@app.route('/store_manager/manage_products')
def manage_products():
    return render_template('product-manager-template.html')

# Route for viewing products
@app.route('/view_products')
def view_products():
    return render_template('view_products.html')

@app.route('/user/shopping', methods=['GET'])
def shopping():
    return render_template('shopping-template.html')

@app.route('/app/decrement-quantity/<int:product_id>', methods=['POST'])
def decrement_quantity(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            if product.Available_Quantity > 0:
                product.Available_Quantity -= 1
                db.session.commit()
                return{"message": "Quantity decremented successfully"}, 200
            else:
                return {"message": "Stock Unavailable"}, 400
        else:
            return {"message": "Product not found"}, 404
    except Exception as e:
        return {"message": "Error decrementing quantity", "error": str(e)}, 500

@app.route('/app/increment-quantity/<int:product_id>',methods=['POST'])
def increment_quantity(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            product.Available_Quantity += 1
            db.session.commit()
            return{"message": "Quantity incremented successfully"}, 200
        else:
            return {"message": "Product not found"}, 404
    except Exception as e:
        return {"message": "Error incrementing quantity", "error": str(e)}, 500

@app.route('/user/carts-list', methods=['GET', 'POST'])
def cart():
    user_id = session['user_id']
    carts = Cart.query.filter_by(User_ID=user_id).all()
    return render_template('cart-list-template.html', Cart=carts)

@app.route('/')
def index():
    return render_template('index.html')

#-----------------------------------------JOBS--------------------------------------------------------------------------------

@app.route('/send_custom_email', methods=['GET', 'POST'])
def send_custom_email():
    try:
        # Get the user's email address from the request
        data = request.get_json()
        to_address = data.get('to_address')
        subject = data.get('subject')
        message = data.get('message')
        content_type = data.get('content_type', 'text')  # Default to plain text

        # Check if the user with the given email address exists
        user = User.query.filter_by(email=to_address).first()
        if user:
            # Send the email
            result = send_email(to_address, subject, message, content_type)
            if result:
                return jsonify({'message': 'Email sent successfully'}), 200
            else:
                return jsonify({'error': 'Failed to send email'}), 500
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_sales_report', methods=['GET'])
def download_sales_report():
    csv_file_path = 'sales_report.csv'
    try:
        products = Product.query.all()
        sales_data = []

        for product in products:
            cart_items = db.session.query(Cart.Cart_Items).filter(Cart.Cart_Items.contains(f'"{product.Product_ID}":')).all()
            
            sales_data.append({
                'Product ID': product.Product_ID,
                'Category Name': product.Category_Name,
                'Product Name': product.Product_Name,
                'Available Quantity': product.Available_Quantity,
                'Rate Per Unit': product.Rate_Per_Unit,
            })

        cart_items_2 = db.session.query(Cart).all()
        for cart_item in cart_items_2:
            sales_data.append({
                    'Cart ID': cart_item.Cart_ID,
                    'User Email': db.session.query(User.email).filter(User.id == cart_item.User_ID).first(),
                    'Purchase Date': cart_item.Purchase_Date,
                    'Total Price': cart_item.Total_Price,
                })
        
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Product ID', 'Category Name', 'Product Name', 'Available Quantity', 'Rate Per Unit', 'Cart ID', 'User Email', 'Purchase Date', 'Total Price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sales_data)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500
    finally:
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
        redirect(url_for('manager_dashboard'))

@celery.task
def send_cart_reminder():
    with app.app_context():
        current_time = datetime.now()
        target_time = current_time.replace(hour=17, minute=0, second=0, microsecond=0)

        if current_time > target_time:
            return

        users_no_cart = User.query.filter_by(role='USER').all()

        for user in users_no_cart:
            cart_entry = Cart.query.filter(
                Cart.User_ID == user.id,
                Cart.Purchase_Date >= datetime.combine(current_time.date(), datetime.min.time()),
                Cart.Purchase_Date < target_time,
            ).first()

            if not cart_entry:
                send_email(
                    user.email,
                    "Cart Reminder",
                    f"Hello {user.email}, don't forget to visit and buy from our app!"
                )

@celery.task
def send_monthly_activity_report():
    with app.app_context():
        today = datetime.now()
    
        #if today.day == 1:
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=30)
        #last_day_of_month = first_day_of_month - timedelta(days=1)

        users = User.query.filter_by(role='USER').all()

        os.environ['WKHTMLTOPDF_PATH'] = '/usr/bin/wkhtmltopdf'

        for user in users:
            cart_orders = Cart.query.filter(
                Cart.User_ID == user.id,
                #Cart.Purchase_Date >= last_day_of_month.replace(day=1),
                Cart.Purchase_Date >= start_date,
                #Cart.Purchase_Date <= last_day_of_month,
                Cart.Purchase_Date <= first_day_of_month,
            ).all()

            if cart_orders:
                env = Environment(loader=FileSystemLoader('templates'))
                template = env.get_template('monthly_activity_report.html')
                html_content = template.render(user=user, cart_orders=cart_orders, today=today)

                # Save HTML content to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
                    temp_html.write(html_content.encode())
                    temp_html_path = temp_html.name

                # Use a temporary file for PDF output
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    pdf_output_path = temp_pdf.name

                # Use the temporary HTML file path
                pdfkit.from_file(temp_html_path, pdf_output_path, options={'quiet': ''})

                # Read the contents of the PDF file into a BytesIO object
                with open(pdf_output_path, 'rb') as pdf_file:
                    pdf_output = BytesIO(pdf_file.read())

                # Remove the temporary HTML and PDF files
                os.remove(temp_html_path)
                os.remove(pdf_output_path)

                subject = f"Monthly Activity Report - {first_day_of_month.strftime('%B %Y')}"
                send_email_monthly(user.email, subject, html_content, attachment_file=pdf_output.read(), content="html")


if __name__ == '__main__':
    with app.app_context():
        initialize_database()
        add_admin()

        celery_thread = threading.Thread(target=celery.worker_main, args=(['worker', '--loglevel=info'],))
        celery_thread.start()

        send_cart_reminder.apply_async(eta=datetime.utcnow() + timedelta(seconds=10))
        send_monthly_activity_report.apply_async(eta=datetime.utcnow() + timedelta(seconds=10))
        
        app.run(debug=True, threaded=True)
