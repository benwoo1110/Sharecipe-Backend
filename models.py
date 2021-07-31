from datetime import date, datetime
import typing

from sqlalchemy.sql.elements import Cast
from app import db
from passlib.hash import pbkdf2_sha256 as sha256
from dataclasses import dataclass
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class EditableDb:

    time_created = db.Column(db.DateTime(), nullable = True)
    time_modified = db.Column(db.DateTime(), nullable = True)

    def add_to_db(self):
        self.time_created = datetime.now()
        self.time_modified = datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        did_change = False
        for attr, data in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, data)
                did_change = True
        if did_change:
            self.time_modified = datetime.now()
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
    profile_image_id: str
    time_created: datetime
    time_modified: datetime

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    bio = db.Column(db.String(512), nullable = True)
    profile_image_id = db.Column(db.String(256), nullable = True)

    def verify_password(self, password) -> bool:
        return sha256.verify(password, self.password_hash)

    def remove_from_db(self):
        # Remove recipe
        for recipe in Recipe.get_for_user_id(self.user_id):
            recipe.remove_from_db(commit=False)

        # Remove follows
        for follow in UserFollow.get_for_user_id(self.user_id):
            db.session.delete(follow)

        # Remove followers
        for follow in UserFollow.get_for_follow_id(self.user_id):
            db.session.delete(follow)

        db.session.commit()

        db.session.delete(self)
        db.session.commit()

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
    def get_for_follow_id(cls, follow_id: int):
        return cls.query.filter_by(follow_id=follow_id).all()

    @classmethod
    def get_by_id(cls, user_id: int, follow_id: int):
        return cls.query.filter_by(user_id=user_id, follow_id=follow_id).first()

    @classmethod
    def get_follows_count(cls, user_id: int) -> int:
        return cls.query.filter_by(user_id=user_id).count()

    @classmethod
    def get_follower_count(cls, follow_id: int) -> int:
        return cls.query.filter_by(follow_id=follow_id).count()


@dataclass
class Recipe(db.Model, EditableDb):
    __tablename__ = 'recipes'

    recipe_id: int
    user_id: int
    name: str
    description: str
    portion: int
    difficulty: int
    total_time_needed: int
    is_public: bool
    icon: 'RecipeImage'
    steps: list
    ingredients: list
    images: list
    tags: list
    time_created: datetime
    time_modified: datetime

    recipe_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    name = db.Column(db.String(256), nullable = False)
    description = db.Column(db.String(2048), nullable = True)
    portion = db.Column(db.Integer, nullable = True)
    difficulty = db.Column(db.Integer, nullable = True)
    total_time_needed = db.Column(db.Integer, nullable = True)
    is_public = db.Column(db.Boolean, unique=False, default=False)
    steps = db.relationship('RecipeStep', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")
    images = db.relationship('RecipeImage', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")
    tags = db.relationship('RecipeTag', backref='recipe', lazy=True, cascade="save-update, merge, delete, delete-orphan")

    @hybrid_property
    def icon(self):
        try:
            return RecipeImage.get_icon(self.recipe_id)
        except NameError:
            # Class loading order is dumb
            return None

    def remove_from_db(self, commit=True):
        # Remove likes
        for like in RecipeLike.get_for_recipe_id(self.recipe_id):
            db.session.delete(like)

        db.session.delete(self)
        
        if commit:
            db.session.commit()

    @classmethod
    def get_for_user_id(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id).all() 

        #TODO dont load all data
        # q = db.session.query(cls.recipe_id, cls.user_id, cls.name).filter_by(user_id=user_id)
        # return [r._asdict() for r in q.all()]

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
        return cls.query.filter(cls.name.contains(name) & cls.is_public == True).all()

        #TODO dont load all data
        # q = db.session.query(cls.recipe_id, cls.user_id, cls.name, cls.icon).filter(cls.name.contains(name) & cls.public == True)
        # return [r._asdict() for r in q.all()]

    @classmethod
    def check_exist(cls, recipe_id: int, user_id: int = None):
        if not user_id:
            return db.session.query(cls.query.filter_by(recipe_id=recipe_id).exists()).scalar()
        return db.session.query(cls.query.filter_by(recipe_id=recipe_id, user_id=user_id).exists()).scalar()

    @classmethod
    def get_count_for_user(cls, user_id: int) -> int:
        return cls.query.filter_by(user_id=user_id).count()


@dataclass
class RecipeStep(db.Model, EditableDb):
    __tablename__ = 'recipe_steps'

    recipe_id: int
    step_number: int
    description: str
    time_created: datetime
    time_modified: datetime

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key = True)
    step_number = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(1024), nullable = True)

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
    time_created: datetime
    time_modified: datetime

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
    time_created: datetime
    time_modified: datetime

    file_id = db.Column(db.String(256), primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))

    @classmethod
    def get_icon(cls, recipe_id: int):
        return cls.query.filter_by(recipe_id=recipe_id).first()

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
    time_created: datetime
    time_modified: datetime

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key = True)
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

    @classmethod
    def get_count_for_user(cls, user_id: int) -> int:
        return cls.query.filter_by(user_id=user_id).count()



@dataclass
class RecipeTag(db.Model, EditableDb):
    __tablename__ = 'recipe_tags'

    tag_id: int
    recipe_id: int
    name: str

    tag_id = db.Column(db.Integer, primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    name = db.Column(db.String(256), nullable = False)

    @classmethod
    def get_top_of(cls, limit: int = 50):
        return cls.query.with_entities(cls.name).distinct(cls.name).limit(limit).all() 


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120), nullable = False)
    revoke_time = db.Column(db.DateTime(), nullable = False)

    def add(self):
        self.revoke_time = datetime.now()
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


@dataclass
class DiscoverSection:

    header: str
    size: str
    recipes: list


@dataclass
class Stats:

    name: str
    number: int
