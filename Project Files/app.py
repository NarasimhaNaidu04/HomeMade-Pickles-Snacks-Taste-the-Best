from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import boto3
import os
import logging
from botocore.exceptions import ClientError
import uuid
from datetime import datetime

# -------------------- Flask Config --------------------

app = Flask(__name__)
app.secret_key = 'pickles123'

# Session configuration
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# -------------------- Logging --------------------

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- DynamoDB Setup ---
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

def create_user_table():
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if 'Users' not in existing_tables:
        dynamodb.create_table(
            TableName='Users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

# ✅ Create table first
create_user_table()

# ✅ THEN define the table object
user_table = dynamodb.Table('Users')
# --- Orders Table Creation ---
def create_orders_table():
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if 'Orders' not in existing_tables:
        dynamodb.create_table(
            TableName='Orders',
            KeySchema=[{'AttributeName': 'order_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'order_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        logger.info("✅ Created 'Orders' table.")

# ✅ Call this after Users table creation
create_orders_table()

# ✅ Define the orders table object
orders_table = dynamodb.Table('Orders')
# Pickle product list (15+ items)
pickle_list = [
    {
        'id': 1,
        'name': 'Mango Pickle',
        'image': 'mango.png',
        'price': 150,
        'desc': 'Tangy mango pickle.',
        'category': 'Traditional',
        'best_seller': True
    },
    {
        'id': 2,
        'name': 'Lemon Pickle',
        'image': 'lemon.png',
        'price': 120,
        'desc': 'Classic lemon pickle.',
        'category': 'Traditional',
        'best_seller': False
    },
    {
        'id': 3,
        'name': 'Garlic Pickle',
        'image': 'garlic.png',
        'price': 140,
        'desc': 'South Indian spicy garlic pickle.',
        'category': 'Spicy',
        'best_seller': True
    },
    {
        'id': 4,
        'name': 'Green Chili Pickle',
        'image': 'chili.png',
        'price': 130,
        'desc': 'Hot green chili pickle.',
        'category': 'Spicy',
        'best_seller': False
    },
    {
        'id': 5,
        'name': 'Sweet Mango Pickle',
        'image': 'sweet-mango.png',
        'price': 160,
        'desc': 'Sweet mango preserve.',
        'category': 'Sweet',
        'best_seller': True
    },
    {
        'id': 6,
        'name': 'Chicken Pickle',
        'image': 'chicken.png',
        'desc': 'Andhra-style chicken pickle – spicy and rich.',
        'price': 200,
        'category': 'Spicy',
        'type': 'Non-Veg',
        'best_seller': True
    },
    {
        'id': 7,
        'name': 'Fish Pickle',
        'image': 'fish.png',
        'desc': 'Coastal special fish pickle with tangy flavor.',
        'price': 220,
        'category': 'Spicy',
        'type': 'Non-Veg'
    },
    {
        'id': 8,
        'name': 'Prawn Pickle',
        'image': 'prawn.png',
        'desc': 'Delicious prawn pickle soaked in spices.',
        'price': 240,
        'category': 'Spicy',
        'type': 'Non-Veg'
    },
    {
        'id': 9,
        'name': 'Mutton Pickle',
        'image': 'mutton.png',
        'desc': 'Tender mutton chunks in spicy gravy.',
        'price': 260,
        'category': 'Spicy',
        'type': 'Non-Veg'
    }
]

# Sample Snacks
snack_list = [
    {
        'id': 101,
        'name': 'Papad',
        'image': 'papad.png',
        'desc': 'Crispy papad to go with pickles',
        'price': 40
    },
    {
        'id': 102,
        'name': 'Fryums',
        'image': 'fryums.png',
        'desc': 'Colorful fryums — kids favorite!',
        'price': 50
    }
]

def get_user_by_email(email):
    try:
        response = user_table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None

def create_user(name, email, password):
    try:
        hashed_pw = generate_password_hash(password)
        user_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': hashed_pw
            }
        )
        return True
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def get_all_users():
    try:
        response = user_table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"❌ Error scanning users: {e}")
        return []
# ---------------- ROUTES ---------------- #

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'], pickles=pickle_list)
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if get_user_by_email(email):
            flash('User already exists!', 'danger')
            return redirect(url_for('signup'))

        if create_user(name, email, password):
            flash('Signup successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Signup failed. Try again.', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/products')
def products():
    filter_type = request.args.get('type', 'all')
    page = int(request.args.get('page', 1))
    items_per_page = 6
    
    # Filter products
    if filter_type == 'veg':
        filtered = [p for p in pickle_list if p['category'] in ['Traditional', 'Sweet']]
    elif filter_type == 'nonveg':
        filtered = [p for p in pickle_list if p.get('type') == 'Non-Veg']
    elif filter_type == 'snacks':
        # No pagination for snacks (optional)
        return render_template('products.html', pickles=[], snacks=snack_list, active='snacks', current_page=1, total_pages=1)
    else:
        filtered = pickle_list
    
    total_items = len(filtered)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated = filtered[start:end]
    
    return render_template('products.html',
                           pickles=paginated,
                           snacks=[],
                           active=filter_type,
                           current_page=page,
                           total_pages=total_pages)

@app.route('/add_to_cart/<int:pid>')
def add_to_cart(pid):
    if 'user' not in session:
        flash("Please login to add items to cart.")
        return redirect(url_for('login'))

    email = session['user']
    cart_key = f'cart_{email}'
    all_products = pickle_list + snack_list
    item = next((p for p in all_products if p['id'] == pid), None)

    if item:
        cart = session.get(cart_key, [])
        for entry in cart:
            if entry['id'] == item['id']:
                entry['quantity'] += 1
                break
        else:
            cart.append({**item, 'quantity': 1})
        session[cart_key] = cart
        session.modified = True
        flash(f"{item['name']} added to cart.")
    else:
        flash("Item not found.")
    return redirect(url_for('index'))


@app.route('/cart')
def view_cart():
    if 'user' not in session:
        return redirect(url_for('view_cart'))

    email = session['user']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('cart.html', items=cart_items, total=total)


@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])

    if 0 <= index < len(cart_items):
        removed_item = cart_items.pop(index)
        flash(f"Removed {removed_item['name']} from cart.")
        session[cart_key] = cart_items
        session.modified = True
    return redirect(url_for('view_cart'))


@app.route('/clear_cart')
def clear_cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    cart_key = f'cart_{email}'
    session.pop(cart_key, None)
    session.modified = True
    flash("Cart cleared.")
    return redirect(url_for('view_cart'))


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])

    index = int(request.form.get('index'))
    action = request.form.get('action')

    if 0 <= index < len(cart_items):
        if action == 'increase':
            cart_items[index]['quantity'] += 1
        elif action == 'decrease':
            cart_items[index]['quantity'] -= 1
            if cart_items[index]['quantity'] <= 0:
                cart_items.pop(index)

    session[cart_key] = cart_items
    session.modified = True
    return redirect(url_for('view_cart'))


# ---------- PLACE ORDER ROUTE ---------- #

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])

    if not cart_items:
        flash("Your cart is empty!")
        return redirect(url_for('index'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    order_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # ✅ Save order to DynamoDB
    try:
        orders_table.put_item(Item={
            'order_id': order_id,
            'email': email,
            'items': cart_items,
            'total': total,
            'timestamp': timestamp
        })
        logger.info(f"✅ Order saved: {order_id} for {email}")
    except Exception as e:
        logger.error(f"❌ Failed to save order: {e}")

    # Clear cart
    session.pop(cart_key, None)
    session.modified = True

    flash("🎉 Order placed successfully!")
    return render_template('success.html')

@app.route('/success')
def success():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('success.html')


@app.route('/admin')
def admin():
    if 'user' in session and session['user'] == 'admin@pickles.com':
        users = get_all_users()
        return render_template('admin.html', users=users)
    flash("❌ Unauthorized access.")
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')


@app.route('/veg_pickles')
def veg_pickles():
    veg_pickles = [p for p in pickle_list if p['category'].lower() in ['traditional', 'sweet']]
    return render_template('veg_pickles.html', pickles=veg_pickles)


@app.route('/non_veg_pickles')
def non_veg_pickles():
    nonveg_pickles = [p for p in pickle_list if p['category'].lower() == 'non-veg']
    return render_template('non_veg_pickles.html', pickles=nonveg_pickles)


@app.route('/snacks')
def snacks():
    return render_template('snacks.html', snacks=snack_list)


# ---------------- RUN APP ---------------- #
if __name__ == '__main__':
    app.run(debug=True)