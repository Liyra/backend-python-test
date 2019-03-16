from alayatodo import app, db
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    abort,
    jsonify,
    url_for
)
from alayatodo.models import Users, Todos
from functools import wraps


ERROR_STRING_404 = 'Resource not found'
PAGINATION_NUMBER = 3


def login_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper


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

    users = Users.query.filter_by(username=username).all()
    for user in users:
        try:
            if user and user.validate_password(password):
                session['user'] = user.to_dict_unsensitive()
                session['logged_in'] = True
                return redirect('/todo')
        except ValueError as e:
            print(e)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<todo_id>', methods=['GET'])
@login_check
def todo(todo_id):
    todo = Todos.query.filter_by(
        user_id=session.get('user')['id'], id=todo_id).first()
    if todo:
        return render_template('todo.html', todo=todo)
    return abort(404, ERROR_STRING_404)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_check
def todos():
    page = request.args.get('page', 1, type=int)
    todos = Todos.query.filter_by(user_id=session.get(
        'user')['id']).paginate(page, PAGINATION_NUMBER, False)
    next_url = url_for(
        'todos', page=todos.next_num) if todos.has_next else None
    prev_url = url_for(
        'todos', page=todos.prev_num) if todos.has_prev else None
    return render_template('todos.html', todos=todos.items, get_flashed_messages=get_flashed_messages,
                           next_url=next_url, prev_url=prev_url)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_check
def todos_POST():
    description = request.form.get('description')
    if not description:
        session['alert'] = ['A description must be provided!']
        return redirect('/todo')
    db.session.add(
        Todos(user_id=session['user']['id'], description=description))
    db.session.commit()
    session['alert'] = ['A todo has been successfully created!']
    return redirect('/todo')


@app.route('/todo/<todo_id>', methods=['POST'])
@login_check
def todo_DELETE(todo_id):
    deleted = Todos.query.filter_by(
        user_id=session.get('user')['id'], id=todo_id).delete()
    db.session.commit()
    if deleted == 1:
        session['alert'] = ['A todo has been successfully deleted!']
        return redirect('/todo')
    return abort(404, ERROR_STRING_404)


@app.route('/todo/<todo_id>/complete', methods=['POST'])
@login_check
def todo_POST(todo_id):
    updated = db.session.query(Todos).filter_by(user_id=session.get(
        'user')['id'], id=todo_id).update({"completed": True})
    db.session.commit()
    if updated == 1:
        return redirect('/todo')
    return abort(404, ERROR_STRING_404)


@app.route('/todo/<todo_id>/json', methods=['GET'])
@login_check
def todo_json(todo_id):
    todo = Todos.query.filter_by(
        user_id=session.get('user')['id'], id=todo_id).first()
    if todo:
        return jsonify(todo.to_dict())
    else:
        return abort(404, ERROR_STRING_404)


def get_flashed_messages():
    alert = session['alert'] if 'alert' in session else []
    session.pop('alert', None)
    return alert
