from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)
app.secret_key = 'pickles123'

# Configure session to be more persistent
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# In-memory storage
users = []
cart = {}
current_id = 1

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

# User management functions
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'], pickles=pickle_list)
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash("❌ Passwords do not match!")
            return render_template('signup.html')
        
        users = load_users()
        
        # check if user exists
        if any(u['email'] == email for u in users):
            flash("⚠️ Email already registered!")
            return render_template('signup.html')
        
        # add new user
        users.append({
            'name': name,
            'email': email,
            'password': password  # store as plaintext now (use hash later)
        })
        save_users(users)
        print(f"✅ New user: {email}")
        flash("Account created successfully! Please login.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        
        if user:
            session['user'] = {
                'email': user['email'],
                'name': user['name']
            }
            return redirect(url_for('products'))
        else:
            flash("❌ Invalid credentials")
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear user's cart when they logout
    if 'user' in session:
        email = session['user']['email']
        cart_key = f'cart_{email}'
        session.pop(cart_key, None)
    
    session.pop('user', None)
    flash("You have been logged out.")
    return redirect(url_for('index'))

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
    
    user_email = session['user']['email']
    cart_key = f"cart_{user_email}"
    
    # Combine all products
    all_products = pickle_list + snack_list
    item = next((p for p in all_products if p['id'] == pid), None)
    
    if item:
        cart = session.get(cart_key, [])
        cart.append(item)
        session[cart_key] = cart
        session.modified = True
        flash(f"✅ {item['name']} added to cart!")
        print(f"✅ Added to cart: {item['name']} for user: {user_email}")
    else:
        flash("❌ Item not found!")
        print(f"❌ Item ID {pid} not found in product list.")
    
    return redirect(url_for('products', type=request.args.get('type', 'all')))

@app.route('/cart')
def view_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])
    
    # Debug: Print cart contents
    print(f"🛒 Viewing cart for {email}")
    print(f"Cart key: {cart_key}")
    print(f"Cart items: {len(cart_items)}")
    print(f"Session keys: {list(session.keys())}")
    
    # Calculate total
    total = sum(item['price'] for item in cart_items)
    
    return render_template('cart.html', items=cart_items, total=total)

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])
    
    if 0 <= index < len(cart_items):
        removed_item = cart_items.pop(index)
        session[cart_key] = cart_items
        session.modified = True
        flash(f"❌ {removed_item['name']} removed from cart!")
    
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    cart_key = f'cart_{email}'
    
    # Clear cart using multiple methods
    session[cart_key] = []
    session.pop(cart_key, None)
    session.modified = True
    
    flash("🗑️ Cart cleared successfully!")
    print(f"🗑️ Cart manually cleared for {email}")
    
    return redirect(url_for('view_cart'))

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    cart_key = f'cart_{email}'
    cart_items = session.get(cart_key, [])
    
    index = int(request.form.get('index'))
    action = request.form.get('action')
    
    if 0 <= index < len(cart_items):
        if action == 'increase':
            # Add another instance of the same item
            cart_items.append(cart_items[index].copy())
            flash(f"➕ Added another {cart_items[index]['name']}")
        elif action == 'decrease':
            # Remove one instance
            removed_item = cart_items.pop(index)
            flash(f"➖ Removed one {removed_item['name']}")
    
    session[cart_key] = cart_items
    session.modified = True
    
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']['email']
    cart_key = f"cart_{email}"
    cart_items = session.get(cart_key, [])
    
    if not cart_items:
        flash("Your cart is empty!")
        return redirect(url_for('products'))
    
    # Calculate total
    total = sum(item['price'] for item in cart_items)
    
    return render_template('checkout.html', items=cart_items, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get user's email to find the cart key
    email = session['user']['email']
    cart_key = f'cart_{email}'
    
    # Get cart items before clearing (for order processing)
    cart_items = session.get(cart_key, [])
    
    if not cart_items:
        flash("Your cart is empty!")
        return redirect(url_for('products'))
    
    # Process order (you can add order saving logic here)
    total = sum(item['price'] for item in cart_items)
    print(f"📦 Order placed by {email} for ₹{total}")
    print(f"Items: {[item['name'] for item in cart_items]}")
    
    # ✅ Clear cart after order - using the same method as clear_cart route
    session[cart_key] = []
    session.pop(cart_key, None)
    session.modified = True
    
    # Add a flag to show clear cart button on success page
    session['show_clear_cart'] = True
    session.modified = True
    
    # Verify cart is cleared
    remaining = session.get(cart_key, [])
    print(f"Cart after clearing: {len(remaining)} items")
    print(f"All session keys after clearing: {list(session.keys())}")
    
    # Set success message
    flash("🎉 Order placed successfully!")
    
    # Render success page directly
    return render_template('success.html')

@app.route('/success')
def success():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('success.html')

@app.route('/admin')
def admin():
    if 'user' in session and session['user']['email'] == 'admin@pickles.com':
        users = load_users()
        return render_template('admin.html', users=users)
    flash("Unauthorized access.")
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/veg_pickles')
def veg_pickles():
    veg_pickles = [p for p in pickle_list if p['category'] in ['Traditional', 'Sweet']]
    return render_template('veg_pickles.html', pickles=veg_pickles)

@app.route('/non_veg_pickles')
def non_veg_pickles():
    nonveg_pickles = [p for p in pickle_list if p.get('type') == 'Non-Veg']
    return render_template('non_veg_pickles.html', pickles=nonveg_pickles)

@app.route('/snacks')
def snacks():
    return render_template('snacks.html', snacks=snack_list)

# ---------------- RUN APP ---------------- #
if __name__ == '__main__':
    app.run(debug=True)