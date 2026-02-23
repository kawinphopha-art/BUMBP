from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-2026'

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'image_url': self.image_url
        }


# Create database tables and insert mock data
with app.app_context():
    db.create_all()
    
    # Insert mock data if products table is empty
    if Product.query.count() == 0:
        mock_products = [
            Product(
                name='Premium Headphones',
                price=2999.00,
                image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop'
            ),
            Product(
                name='Smart Watch',
                price=3499.00,
                image_url='https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop'
            ),
            Product(
                name='Designer Sunglasses',
                price=1899.00,
                image_url='https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=300&fit=crop'
            ),
            Product(
                name='Portable Speaker',
                price=1499.00,
                image_url='https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=300&fit=crop'
            )
        ]
        db.session.add_all(mock_products)
        db.session.commit()
        print('✓ Mock data inserted successfully!')


# Routes

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (admin/1234)
        if username == 'admin' and password == '1234':
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin.html', products=products)


@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        
        new_product = Product(
            name=name,
            price=float(price),
            image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_product.html')


@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
