import json
from alayatodo import app, db
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    abort,
    jsonify
    )
from alayatodo.models import Users, Todos


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

    user = Users.query.filter_by(username=username, password=password).one()
    if user:
        session['user'] = user.to_dict()
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
    todo = Todos.query.filter_by(user_id=session.get('user')['id'], id=id).one()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    todos = Todos.query.filter_by(user_id=session.get('user')['id']).all()
    return render_template('todos.html', todos=todos, get_flashed_messages=get_flashed_messages)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', None)
    if description is None or description is '':
        session['alert'] = ['A description must be provided!']
        return redirect('/todo')
    db.session.add(Todos(user_id=session['user']['id'], description=description))
    db.session.commit()
    session['alert'] = ['A todo has been successfully created!']
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_DELETE(id):
    if not session.get('logged_in'):
        return redirect('/login')
    Todos.query.filter_by(id=id).delete()
    db.session.commit()
    session['alert'] = ['A todo has been successfully deleted!']
    return redirect('/todo')


@app.route('/todo/<id>/complete', methods=['POST'])
def todo_POST(id):
    if not session.get('logged_in'):
        return redirect('/login')
    db.session.query(Todos).filter_by(user_id=session.get('user')['id'], id=id).update({ "completed": True})
    db.session.commit()
    return redirect('/todo')


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter_by(user_id=session.get('user')['id'], id=id).one()
    return jsonify(todo.to_dict())


def get_flashed_messages():
    alert = session['alert'] if 'alert' in session else []
    session.pop('alert', None)
    return alert