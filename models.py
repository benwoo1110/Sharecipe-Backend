from datetime import datetime
import typing
from app import db
from passlib.hash import pbkdf2_sha256 as sha256
from dataclasses import dataclass


class EditableDb:
    def add_to_db(self):
        self.time_created = datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for attr, data in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, data)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()


@dataclass
class User(db.Model, EditableDb):
    __tablename__ = 'users'

    user_id: int
    username: str
    bio: str
    time_created: datetime
    profile_image_id: str

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    bio = db.Column(db.String(512), nullable = True)
    profile_image_id = db.Column(db.String(256), nullable = True)
    time_created = db.Column(db.DateTime(), nullable = False)

    def verify_password(self, password) -> bool:
        return sha256.verify(password, self.password_hash)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(user_id = user_id).first()

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    @classmethod
    def get_all_of_ids(cls, user_ids: list):
        return cls.query.filter(not user_ids or cls.user_id in user_ids).all()

    @classmethod
    def get_all_public(cls, name):
        return cls.query.filter(cls.username.contains(name)).all()

    @classmethod
    def check_exist(cls, user_id: int):
        return db.session.query(cls.query.filter_by(user_id=user_id).exists()).scalar()

    @staticmethod
    def hash_password(password):
        return sha256.hash(password)


@dataclass
class UserFollow(db.Model, EditableDb):
    __tablename__ = 'user_follows'

    user_id: int
    follow_id: int

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)
    follow_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)

    @classmethod
    def get_for_user_id(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_by_id(cls, user_id: int, follow_id: int):
        return cls.query.filter_by(user_id=user_id, follow_id=follow_id).first()

@dataclass
class Recipe(db.Model, EditableDb):
    __tablename__ = 'recipes'

    recipe_id: int
    user_id: int
    name: str
    portion: int
    difficulty: int
    total_time_needed: int
    time_created: datetime
    public: bool
    steps: list
    ingredients: list
    images: list

    recipe_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    name = db.Column(db.String(256), nullable = False)
    portion = db.Column(db.Integer, nullable = True)
    difficulty = db.Column(db.Integer, nullable = True)
    total_time_needed = db.Column(db.Integer, nullable = True)
    public = db.Column(db.Boolean, unique=False, default=True)
    time_created = db.Column(db.DateTime(), nullable = False)
    steps = db.relationship('RecipeStep', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")
    images = db.relationship('RecipeImage', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")

    @classmethod
    def get_for_user_id(cls, user_id: int):
        q = db.session.query(cls.recipe_id, cls.user_id, cls.name).filter_by(user_id=user_id)
        return [r._asdict() for r in q.all()]

    @classmethod
    def get_by_id(cls, recipe_id: int, user_id: int = None):
        if not user_id:
            return cls.query.filter_by(recipe_id=recipe_id).first()
        return cls.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()

    @classmethod
    def get_by_name(cls, name: str):
        return cls.query.filter(cls.name.startswith(name)).all()

    @classmethod
    def get_all_public(cls, name):
        q = db.session.query(cls.recipe_id, cls.user_id, cls.name).filter(cls.name.contains(name) & cls.public == True)
        return [r._asdict() for r in q.all()]

    @classmethod
    def check_exist(cls, recipe_id: int, user_id: int = None):
        if not user_id:
            return db.session.query(cls.query.filter_by(recipe_id=recipe_id).exists()).scalar()
        return db.session.query(cls.query.filter_by(recipe_id=recipe_id, user_id=user_id).exists()).scalar()


@dataclass
class RecipeStep(db.Model, EditableDb):
    __tablename__ = 'recipe_steps'

    recipe_id: int
    step_number: int
    name: str
    description: str
    time_needed: int

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key = True)
    step_number = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256), nullable = False)
    description = db.Column(db.String(1024), nullable = True)
    time_needed = db.Column(db.Integer, nullable = True)

    @classmethod
    def get_for_recipe_id(cls, recipe_id: int):
        return cls.query.filter_by(recipe_id=recipe_id).all()

    @classmethod
    def get_by_id(cls, recipe_id: int, step_number: int):
        return cls.query.filter_by(recipe_id=recipe_id, step_number=step_number).first()


@dataclass
class RecipeIngredient(db.Model, EditableDb):
    __tablename__ = 'recipe_ingredients'

    ingredient_id: int
    recipe_id: int
    name: str
    quantity: int
    unit: str

    ingredient_id = db.Column(db.Integer, primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    name = db.Column(db.String(256), nullable = False)
    quantity = db.Column(db.Integer, nullable = True)
    unit = db.Column(db.String(32), nullable = True)


@dataclass
class RecipeImage(db.Model, EditableDb):
    __tablename__ = 'recipe_images'

    file_id: str
    recipe_id: int

    file_id = db.Column(db.String(256), primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))

    @classmethod
    def get_for_recipe_id(cls, recipe_id: set):
        return cls.query.filter(RecipeImage.recipe_id == recipe_id).all()

    @classmethod
    def get_for_ids(cls, file_ids: typing.Union[list, set]):
        return cls.query.filter(RecipeImage.file_id in file_ids).all()

    @classmethod
    def get_by_id(cls, recipe_id: int, file_id: str = None):
        if file_id:
            return cls.query.filter_by(file_id=file_id, recipe_id=recipe_id).first()
        return cls.query.filter_by(recipe_id=recipe_id).first()

    @classmethod
    def check_exist(cls, file_id: str, recipe_id: int):
        return db.session.query(cls.query.filter_by(file_id=file_id, recipe_id=recipe_id).exists()).scalar()


@dataclass
class RecipeLike(db.Model, EditableDb):
    __tablename__ = 'recipe_likes'

    recipe_id: int
    user_id: int

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)

    @classmethod
    def get_for_recipe_id(cls, recipe_id: int):
        return cls.query.filter_by(recipe_id=recipe_id).all()

    @classmethod
    def get_for_user_id(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_by_id(cls, recipe_id: int, user_id: int):
        return cls.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()


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
