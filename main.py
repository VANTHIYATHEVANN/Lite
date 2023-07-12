from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    manufacture_date = db.Column(db.Date, nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


@app.route('/')
def index():
    return redirect('/user_dashboard')


@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        search_query = request.form['search_query']
        search_type = request.form['search_type']

        if search_type == 'categories':
            categories = Category.query.filter(Category.name.ilike(f'%{search_query}%')).all()
            return render_template('user_dashboard.html', categories=categories)

        elif search_type == 'products':
            products = Product.query.join(Category).filter(
                db.or_(Product.name.ilike(f'%{search_query}%'), Category.name.ilike(f'%{search_query}%'))).all()
            return render_template('user_dashboard.html', products=products)

        elif 'add_to_cart' in request.form:
            product_id = request.form['product_id']
            quantity = int(request.form['quantity'])
            product = Product.query.get(product_id)

            if product:
                item = {
                    'product_id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity
                }
                session['cart'].append(item)
    categories = Category.query.all()
    products = Product.query.join(Category).all()

    return render_template('user_dashboard.html', categories=categories, products=products)


def delete_product():
    if 'admin_id' not in session:
        return redirect('/admin_login')

    product_id = request.form['product_id']
    product = Product.query.get(product_id)
    if product:
        # Remove the product from the database
        db.session.delete(product)
        db.session.commit()
    return redirect('/admin_dashboard')

def edit_product():
    if 'admin_id' not in session:
        return redirect('/admin_login')

    product_id = request.form['product_id']
    product = Product.query.get(product_id)
    if product:
        # Update the product details
        product.name = request.form['product_name']
        product.price = float(request.form['product_price'])
        product.manufacture_date = request.form['manufacture_date']
        product.available_quantity = int(request.form['available_quantity'])
        db.session.commit()
    return redirect('/admin_dashboard')
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session['admin_id'] = admin.id
            return redirect('/admin_dashboard')
        else:
            return redirect('/admin_login')

    return render_template('admin_login.html')


if __name__ == '__main__':
    app.run(debug=True)
