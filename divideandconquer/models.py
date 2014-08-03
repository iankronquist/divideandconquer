from divideandconquer import db

class User(db.Model):
    __tablename__ = "users"
    uid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    salt = db.Column(db.String)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.uid

class Response(db.Model):
    __tablename__ = "responses"
    # is_spam is a trinary value
    # 1 is true
    # 2 is false
    # 3 is unknown
    is_spam = db.Column(db.Integer)
    json_hash = db.Column(db.Text, primary_key=True)
    json = db.Column(db.String)
    classified_by = db.Column(db.ForeignKey('users.name'))
