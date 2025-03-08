from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pin_no = db.Column(db.String(10), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def check_user():
    if request.method == 'POST':
        pin_no = request.form.get('pin_no')
        user = User.query.filter_by(pin_no=pin_no).first()

        if user:
            return render_template('index.html', message="Account already exists!", pin_no=pin_no)
        else:
            new_user = User(pin_no=pin_no, balance=0.0)
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', message="New account created successfully!", pin_no=pin_no)

    return render_template('index.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == "POST":
        pin_no = request.form.get("pin_no")
        amount = request.form.get("dep_amt")

        user = User.query.filter_by(pin_no=pin_no).first()
        if not user:
            return render_template('deposit.html', error="Account not found!")

        if not amount or float(amount) <= 0:
            return render_template('deposit.html', error="Invalid deposit amount!", pin_no=pin_no)

        user.balance += float(amount)
        db.session.commit()
        return render_template('deposit.html', success=f"₹{amount} Deposited Successfully!", pin_no=pin_no, balance=user.balance)

    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == "POST":
        pin_no = request.form.get("pin_no")
        amount = request.form.get("with_amt")

        user = User.query.filter_by(pin_no=pin_no).first()
        if not user:
            return render_template('withdraw.html', error="Account not found!")

        if not amount or float(amount) <= 0:
            return render_template('withdraw.html', error="Invalid withdrawal amount!", pin_no=pin_no)

        if user.balance < float(amount):
            return render_template('withdraw.html', error="Insufficient balance!", pin_no=pin_no)

        user.balance -= float(amount)
        db.session.commit()
        return render_template('withdraw.html', success=f"₹{amount} Withdrawn Successfully!", pin_no=pin_no, balance=user.balance)

    return render_template('withdraw.html')

@app.route('/balance/<pin_no>', methods=['GET'])
def check_balance(pin_no):
    user = User.query.filter_by(pin_no=pin_no).first()
    if user:
        return render_template('balance.html', balance=user.balance, pin_no=pin_no)
    return render_template('balance.html', error="Account not found!")

if __name__ == "__main__":
    app.run(debug=True)
