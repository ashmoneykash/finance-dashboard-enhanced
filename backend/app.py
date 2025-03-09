from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'  # Database file will be created in the project directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Define the Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))

# Create the database tables
with app.app_context():
    db.create_all()

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Finance Dashboard!"})

# User registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful", "user_id": user.id}), 200

# Add an expense route
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    category = data.get('category')
    amount = data.get('amount')
    description = data.get('description')

    if not user_id or not date or not category or not amount:
        return jsonify({"error": "Missing required fields"}), 400

    new_expense = Expense(user_id=user_id, date=date, category=category, amount=amount, description=description)
    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "Expense added successfully"}), 201

# Get all expenses for a user
@app.route('/expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    expense_list = []
    for expense in expenses:
        expense_list.append({
            "id": expense.id,
            "date": expense.date,
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description
        })

    return jsonify({"expenses": expense_list}), 200

# Visualization route
@app.route('/visualize/<int:user_id>', methods=['GET'])
def visualize(user_id):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    if not expenses:
        return jsonify({"error": "No expenses found"}), 404

    # Convert expenses to a DataFrame
    data = {
        "Date": [expense.date for expense in expenses],
        "Category": [expense.category for expense in expenses],
        "Amount": [expense.amount for expense in expenses]
    }
    df = pd.DataFrame(data)

    # Group expenses by category and sum the amounts
    grouped_data = df.groupby("Category")["Amount"].sum().reset_index()

    # Convert the grouped data to a dictionary
    chart_data = {
        "categories": grouped_data["Category"].tolist(),
        "amounts": grouped_data["Amount"].tolist()
    }

    return jsonify(chart_data), 200

# Delete an expense route
@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "Expense deleted successfully"}), 200

# Update an expense route
@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    expense.date = data.get('date', expense.date)
    expense.category = data.get('category', expense.category)
    expense.amount = data.get('amount', expense.amount)
    expense.description = data.get('description', expense.description)

    db.session.commit()

    return jsonify({"message": "Expense updated successfully"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)