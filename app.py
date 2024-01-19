from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATABASE = "todos.db"

def get_user_id(username):
    con = sqlite3.connect(DATABASE)
    cur = con.execute("SELECT user_id FROM users WHERE user_name = ?", (username,))
    user_id = cur.fetchone()
    con.close()
    return user_id[0] if user_id else None

def get_todos(user_id):
    con = sqlite3.connect(DATABASE)
    cur = con.execute("SELECT * FROM todos WHERE user_id = ?", (user_id,))
    todos = [{"idx": row[0], "todo": row[1], "status": row[2]} for row in cur]
    con.close()
    return todos

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    user_id = get_user_id(session['username'])
    todos = get_todos(user_id)

    return render_template("index.html", todos=todos)

@app.route('/add', methods=["POST"])
def add():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    if not request.form['name']:
        return redirect("/")

    user_id = get_user_id(session['username'])

    con = sqlite3.connect(DATABASE)
    con.execute("INSERT INTO todos(todo, user_id) VALUES (?, ?)", (request.form['name'], user_id))
    con.commit()
    con.close()

    return redirect("/")

@app.route('/delete', methods=["POST"])
def delete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    con = sqlite3.connect(DATABASE)

    for e in request.form.getlist('target'):
        con.execute("DELETE FROM todos WHERE id = ?", (e,))

    con.commit()
    con.close()

    return redirect("/")

@app.route('/complete', methods=["POST"])
def complete():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    con = sqlite3.connect(DATABASE)

    for e in request.form.getlist('target'):
        con.execute("UPDATE todos SET status = 1 WHERE id = ?", (e,))

    con.commit()
    con.close()

    return redirect(url_for('index'))

@app.route('/undo', methods=["POST"])
def undo():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    con = sqlite3.connect(DATABASE)

    for e in request.form.getlist('target'):
        con.execute("UPDATE todos SET status = 0 WHERE id = ?", (e,))

    con.commit()
    con.close()

    return redirect(url_for('index'))

@app.route('/login')
def show_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    con = sqlite3.connect(DATABASE)
    cur = con.execute("SELECT * FROM users WHERE user_name = ? AND user_password = ?", (username, hashed_password))
    user = cur.fetchone()
    con.close()

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
    username = request.form['username']
    password = request.form['password']

    con = sqlite3.connect(DATABASE)
    cur = con.execute("SELECT * FROM users WHERE user_name = ?", (username,))
    existing_user = cur.fetchone()
    con.close()

    if existing_user:
        flash('ユーザー名は既に使用されています。別のユーザー名を選択してください。', 'error')
        return redirect(url_for('show_register'))
    else:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        con = sqlite3.connect(DATABASE)
        con.execute("INSERT INTO users(user_name, user_password) VALUES (?, ?)", (username, hashed_password))
        con.commit()
        con.close()

        return redirect(url_for('show_login'))
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
