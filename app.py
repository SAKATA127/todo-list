from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  # SQLite3のデータベースを指定

db = SQLAlchemy(app)  # SQLAlchemyのオブジェクトを作成

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.String(64), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# データベースの初期化
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user = User.query.filter_by(user_name=session['username']).first()
    todos = Todo.query.filter_by(user_id=user.id).all()

    return render_template("index.html", todos=todos)

@app.route('/add', methods=["POST"])
def add():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    if not request.form['name']:
        return redirect("/")

    user = User.query.filter_by(user_name=session['username']).first()

    new_todo = Todo(todo=request.form['name'], user_id=user.id)
    db.session.add(new_todo)
    db.session.commit()

    return redirect("/")

@app.route('/delete', methods=["POST"])
def delete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user = User.query.filter_by(user_name=session['username']).first()

    for e in request.form.getlist('target'):
        todo_to_delete = Todo.query.filter_by(id=e, user_id=user.id).first()
        db.session.delete(todo_to_delete)

    db.session.commit()

    return redirect("/")

@app.route('/complete', methods=["POST"])
def complete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user = User.query.filter_by(user_name=session['username']).first()

    for e in request.form.getlist('target'):
        todo_to_complete = Todo.query.filter_by(id=e, user_id=user.id).first()
        todo_to_complete.status = 1

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/undo', methods=["POST"])
def undo():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user = User.query.filter_by(user_name=session['username']).first()

    for e in request.form.getlist('target'):
        todo_to_undo = Todo.query.filter_by(id=e, user_id=user.id).first()
        todo_to_undo.status = 0

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/login')
def show_login():
    return render_template('login.html')

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

@app.route('/register')
def show_register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if 'username' in session:
        # 既にログインしている場合はToDoリストにリダイレクト
        return redirect(url_for('index'))

    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    new_user = User(user_name=username, user_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session['username'] = username
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0', port=5000)
