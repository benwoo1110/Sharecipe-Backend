from datetime import datetime
from app import db
from passlib.hash import pbkdf2_sha256 as sha256


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    bio = db.Column(db.String(512), nullable = True)
    time_created = db.Column(db.DateTime())

    def add_to_db(self):
        self.time_created = datetime.now()
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, password) -> bool:
        return sha256.verify(password, self.password_hash)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(user_id = user_id).first()

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    @classmethod
    def search_username(cls, username):
        return cls.query.filter(cls.username.startswith(username)).all()

    @staticmethod
    def hash_password(password):
        return sha256.hash(password)

class Recipe(db.Model):
    __tablename__ = 'recipes'

    recipe_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    portion = db.Column(db.Integer, nullable = True)
    total_time_needed = db.Column(db.Integer, nullable = True)


class RecipeStep(db.Model):
    __tablename__ = 'recipe_steps'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key = True)
    step_number = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(1024), primary_key = True)
    time_needed = db.Column(db.Integer, nullable = True)


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120), nullable = False)

    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)
