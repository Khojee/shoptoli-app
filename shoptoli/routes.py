# shoptoli/routes.py
import pycountry
from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Customer, Address, Product, Order, OrderItem
from . import bcrypt # Import bcrypt from our __init__.py

# Use Blueprint to organize routes
main = Blueprint('main', __name__)

@main.route('/')
def index():
    top_products = Product.query.limit(4).all()
    return render_template('index.html', products=top_products)

@main.route('/products')
def products():
    all_products = Product.query.order_by(Product.name).all()
    return render_template('products.html', products=all_products)

# In shoptoli/routes.py, update the register route

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        # ... (code to get form data and check for existing user is the same) ...
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # --- SIMPLIFIED LOGIC ---
        new_user = User(full_name=full_name, email=email, hashed_password=hashed_password)
        new_customer = Customer(user=new_user, phone=request.form.get('phone')) # We'll add phone to the form
        
        # No more address creation here!
        
        db.session.add(new_user)
        # new_customer is automatically added by the cascade relationship
        
        db.session.commit()
        
        flash('Your account has been created! You can now log in and add a shipping address.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.hashed_password, password):
            login_user(user, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    session.pop('cart', None)
    return redirect(url_for('main.index'))

@main.route('/account', methods=['GET', 'POST']) # Allow POST for the form
@login_required
def account():
    # --- This is the new logic for the address form ---
    if request.method == 'POST':
        new_address = Address(
            customer_id=current_user.customer.customer_id,
            street=request.form.get('street'),
            city=request.form.get('city'),
            region=request.form.get('region'),
            postal_code=request.form.get('postal_code'),
            country=request.form.get('country')
        )
        db.session.add(new_address)
        db.session.commit()
        flash('New address has been saved!', 'success')
        return redirect(url_for('main.account'))
    orders = Order.query.filter_by(customer_id=current_user.customer.customer_id).order_by(Order.order_date.desc()).all()
    countries = [(country.name, country.name) for country in pycountry.countries]
    countries.sort(key=lambda x: x[1])
    return render_template('account.html', orders=orders, countries=countries)

# Add this new route in shoptoli/routes.py

@main.route('/account/add_address', methods=['POST'])
@login_required
def add_address():
    new_address = Address(
        customer_id=current_user.customer.customer_id,
        street=request.form.get('street'),
        city=request.form.get('city'),
        region=request.form.get('region'),
        postal_code=request.form.get('postal_code'),
        country=request.form.get('country')
    )
    db.session.add(new_address)
    db.session.commit()
    flash('New address has been saved!', 'success')
    return redirect(url_for('main.account'))

@main.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    session.modified = True
    flash('Item added to cart!', 'success')
    return redirect(url_for('main.products'))

@main.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session.modified = True
        flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))

@main.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)

    cart_product_ids = session['cart'].keys()
    products_in_cart = Product.query.filter(Product.product_id.in_(cart_product_ids)).all()

    cart_items = []
    total_price = 0
    for product in products_in_cart:
        quantity = session['cart'][str(product.product_id)]
        item_total = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })
        total_price += item_total

    return render_template('cart.html', cart_items=cart_items, total=total_price)

@main.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('main.cart'))

    # Get user's addresses
    addresses = current_user.customer.addresses

    # Prepare cart details for summary display (this is copied from the /cart route)
    cart_product_ids = session['cart'].keys()
    products_in_cart = Product.query.filter(Product.product_id.in_(cart_product_ids)).all()
    cart_items = []
    total_price = 0
    for product in products_in_cart:
        quantity = session['cart'][str(product.product_id)]
        item_total = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })
        total_price += item_total

    return render_template('checkout.html', addresses=addresses, cart_items=cart_items, total=total_price)


# CREATE THIS NEW ROUTE
@main.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('main.cart'))
    
    # Get the selected address_id from the form
    selected_address_id = request.form.get('address_id')
    if not selected_address_id:
        flash('Please select a shipping address.', 'danger')
        return redirect(url_for('main.checkout'))

    # The rest of the logic is the same as the old checkout function
    cart_product_ids = cart.keys()
    products_in_cart = Product.query.filter(Product.product_id.in_(cart_product_ids)).all()
    total_amount = 0
    order_items_to_create = []

    for product in products_in_cart:
        quantity = cart[str(product.product_id)]
        if product.stock_quantity < quantity:
            flash(f'Not enough stock for {product.name}.', 'danger')
            return redirect(url_for('main.cart'))
        unit_price = product.price
        total_amount += unit_price * quantity
        order_items_to_create.append({'product_id': product.product_id, 'quantity': quantity, 'unit_price': unit_price})
        product.stock_quantity -= quantity
    
    new_order = Order(
        customer_id=current_user.customer.customer_id, 
        address_id=selected_address_id, # Use the selected address
        total_amount=total_amount
    )
    db.session.add(new_order)
    db.session.commit()

    for item_data in order_items_to_create:
        order_item = OrderItem(order_id=new_order.order_id, **item_data)
        db.session.add(order_item)
    db.session.commit()
    
    session.pop('cart', None)
    flash('Thank you! Your order has been placed.', 'success')
    return redirect(url_for('main.account'))