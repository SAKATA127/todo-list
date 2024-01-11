from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route('/', methods=["GET"])
def list():
    con = sqlite3.connect('todos.db')
    cur = con.execute("select * from todos")
    todos = {}
    for row in cur:
        todos[row[0]] = row[1]
    con.close()
    return render_template("index.html", todos=todos)

@app.route('/add', methods=['POST'])
def add():
    if not request.form['name']:
        return redirect("/")
    con = sqlite3.connect('todos.db')
    con.execute("insert into todos(todo) values (?)", (request.form['name'],))
    con.commit()
    con.close()
    return redirect("/")

@app.route('/delete', methods=["POST"])
def delete():
    con = sqlite3.connect('todos.db')
    for e in request.form:
        con.execute("delete from todos where id = ?", (e,))
    con.commit()
    con.close()
    return redirect("/")

if __name__ == "__main__":
    # 外部からアクセス可能にするためにhost='0.0.0.0'を使用し、ポート80以外を選択
    app.run(debug=True, host='0.0.0.0', port=5000)