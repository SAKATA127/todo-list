from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/', methods=["GET"])
def list():
    con = sqlite3.connect('todos.db')
    cur = con.execute("select * from todos")
    todos=[]
    for row in cur:
        todo ={'idx': row[0], 'todo': row[1], 'status':row[2]}
        todos.append(todo)
    return render_template("index.html", todos=todos)

@app.route('/add', methods=["POST"])
def add():
    if not request.form['name']:
        return redirect("/")
    con = sqlite3.connect('todos.db')
    con.execute("insert into todos(todo) values (?)", (request.form['name'],))
    con.commit()
    return redirect("/")
    
@app.route('/delete', methods=["POST"])
def delete():
    con = sqlite3.connect('todos.db')
    for e in request.form.getlist('target'):
        con.execute("delete from todos where id = ?", (e,))
    con.commit()
    return redirect("/")

@app.route('/complete', methods=["POST"])
def complete():
    con = sqlite3.connect('todos.db')
    for e in request.form.getlist('target'):
        con.execute("update todos set status = '1' where id = ?", (e,))
    con.commit()
    return redirect(url_for('list'))

@app.route('/undo', methods=["POST"])
def undo():
    con = sqlite3.connect('todos.db')
    for e in request.form.getlist('target'):
        con.execute("update todos set status = '0' where id = ?", (e,))
    con.commit()
    return redirect(url_for('list'))

if __name__ == "__main__":
    # 外部からアクセス可能にするためにhost='0.0.0.0'を使用し、ポート80以外を選択
    app.run(debug=True, host='0.0.0.0', port=5000)