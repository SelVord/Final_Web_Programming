from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    name = request.form.get("name")
    psw = request.form.get("psw")
    res = cur.execute(f"SELECT * FROM users WHERE name = '{name}' AND password = '{psw}'").fetchone()
    if res == None:
        return render_template("index.html", error = "Invalid name of password")
    else:
        session['user_id'] = res[0]
        session['user_name'] = res[1]
        tasks = cur.execute(f"SELECT * FROM tasks WHERE user_id = '{res[0]}'").fetchall()
        return render_template("task_manager.html", user = session['user_id'], name = session['user_name'], tasks = tasks)
        # return render_template("index.html", qwee = res)

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/task_manager_reg", methods = ["POST", "GET"])
def task_manager_reg():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    name = request.form.get("name")
    psw = request.form.get("psw")
    psw2 = request.form.get("psw2")
    if psw == psw2 and name != '' and psw != '':
        cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, psw))
        con.commit()
        return render_template("index.html")
    else:
        return render_template("registration.html", error = "Invalid name or password")

@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Удаляем идентификатор пользователя из сессии
    return redirect(url_for('index'))

@app.route("/filter", methods = ["POST", "GET"])
def filter():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    filter = request.form.get("filter")
    if filter == "all":
        tasks = cur.execute(f"SELECT * FROM tasks WHERE user_id = '{session['user_id']}'").fetchall()
    elif filter == "active":
        tasks = cur.execute(f"SELECT * FROM tasks WHERE user_id = '{session['user_id']}' AND status = '0'").fetchall()
    else:
        tasks = cur.execute(f"SELECT * FROM tasks WHERE user_id = '{session['user_id']}' AND status = '1'").fetchall()
    return render_template("task_manager.html", user = session["user_id"], tasks = tasks, name = session["user_name"])

@app.route("/create_task")
def create_task():
    return render_template("create_task.html", name = session["user_name"])

@app.route("/home")
def home():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    tasks = cur.execute(f"SELECT * FROM tasks WHERE user_id = '{session['user_id']}'").fetchall()
    return render_template("task_manager.html", user = session["user_id"], tasks = tasks, name = session["user_name"])

@app.route("/create", methods = ["POST", "GET"])
def create():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("deadline1")
    time = request.form.get("deadline2")
    cur.execute("INSERT INTO tasks (user_id, title, description, status, deadline) VALUES (?, ?, ?, ?, ?)", (session["user_id"], title, description, 0, date + " " + time))
    con.commit()
    return redirect(url_for("home"))

@app.route("/task_detail", methods = ["POST", "GET"])
def task_detail():
    id = request.form.get("id")
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    task = cur.execute(f"SELECT * FROM tasks WHERE id = '{id}'").fetchone()
    datetime = task[5].split()
    return render_template("task.html", task = task, name = session["user_name"], datetime = datetime)

@app.route("/done_undone/<int:id>")
def done_undone(id):
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    stat = cur.execute(f"SELECT status FROM tasks WHERE id = '{id}'").fetchone()
    if stat[0] == 0:
        cur.execute(f"UPDATE tasks SET status = {1} WHERE id = {id}")
    else:
        cur.execute(f"UPDATE tasks SET status = {0} WHERE id = '{id}'")
    con.commit()
    task = cur.execute(f"SELECT * FROM tasks WHERE id = '{id}'").fetchone()
    datetime = task[5].split()
    return render_template("task.html", task = task, name = session["user_name"], datetime = datetime)

@app.route("/edit", methods = ["POST", "GET"])
def edit():
    con = sqlite3.connect("task_manager.db")
    cur = con.cursor()
    id = request.form.get("id")
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("deadline1")
    time = request.form.get("deadline2")
    cur.execute("UPDATE tasks SET title = ?, description = ?, deadline = ? WHERE id = ?", (title, description, date + " " + time, id))
    con.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug = True)
