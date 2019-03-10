from alayatodo import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    todos = db.relationship('Todos', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def to_dict_unsensitive(self):
        return { 'id': self.id, 'username': self.username }


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Todos {}>'.format(self.id)

    def to_dict(self):
        return { 'id': self.id, 'user_id': self.user_id, 'description': self.description, 'completed': self.completed }