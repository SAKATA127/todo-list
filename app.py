from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), unique=True, nullable=False)
    user_password = db.Column(db.String(64), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_request
def before_request():
    if request.endpoint == 'create_tables':
        return
    db.create_all()

def get_user_id(username):
    user = User.query.filter_by(user_name=username).first()
    return user.id if user else None

def get_todos(user_id):
    todos = Todo.query.filter_by(user_id=user_id).all()
    return [{"idx": todo.id, "todo": todo.todo, "status": todo.status} for todo in todos]

@app.route('/add', methods=["POST"])
def add():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    if not request.form['name']:
        return redirect("/")

    user_id = get_user_id(session['username'])

    todo = Todo(todo=request.form['name'], user_id=user_id)
    db.session.add(todo)
    db.session.commit()

    return redirect("/")

@app.route('/delete', methods=["POST"])
def delete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    for e in request.form.getlist('target'):
        todo = Todo.query.get(e)
        db.session.delete(todo)

    db.session.commit()

    return redirect("/")

@app.route('/complete', methods=["POST"])
def complete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    for e in request.form.getlist('target'):
        todo = Todo.query.get(e)
        todo.status = True

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/undo', methods=["POST"])
def undo():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    for e in request.form.getlist('target'):
        todo = Todo.query.get(e)
        todo.status = False

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    user = User.query.filter_by(user_name=username, user_password=hashed_password).first()

    if user:
        session['username'] = username
        return redirect(url_for('index'))
    else:
        flash('ユーザー名またはパスワードが間違っています。', 'error')
        return redirect(url_for('show_login'))

@app.route('/register', methods=['POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    try:
        user = User(user_name=username, user_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        flash('ユーザー登録が完了しました。', 'success')
        return redirect(url_for('login'))
    except:
        flash('ユーザー名が既に使用されています。', 'error')
        return redirect(url_for('show_register'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user_id = get_user_id(session['username'])
    todos = get_todos(user_id)

    return render_template("index.html", todos=todos)

@app.route('/login')
def show_login():
    return render_template('login.html')

@app.route('/register')
def show_register():
    return render_template('register.html')

#if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0', port=5000)
