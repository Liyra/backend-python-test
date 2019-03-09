from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    abort,
    jsonify
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE id = '%s' AND user_id = '%s'" % (id, session.get('user')['id']))
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE user_id = '%s'" % session.get('user')['id'])
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos, get_flashed_messages=get_flashed_messages)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', None)
    if description is None or description is '':
        abort(400, 'A description must be provided')
    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
        % (session['user']['id'], description)
    )
    g.db.commit()
    session['alert'] = ['A todo has been successfully created!']
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_DELETE(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s' AND user_id = '%s'" % (id, session.get('user')['id']))
    g.db.commit()
    session['alert'] = ['A todo has been successfully deleted!']
    return redirect('/todo')


@app.route('/todo/<id>/complete', methods=['POST'])
def todo_POST(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET completed=1 WHERE id ='%s' AND user_id = '%s'" % (id, session.get('user')['id']))
    g.db.commit()
    return redirect('/todo')


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s' AND user_id = '%s'" % (id, session.get('user')['id']))
    return jsonify(dict(zip([column[0] for column in cur.description], cur.fetchone())))


def get_flashed_messages():
    alert = session['alert'] if 'alert' in session else []
    session.pop('alert', None)
    return alert