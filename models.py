from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128), unique = True, nullable = False)
    password = db.Column(db.String(64), nullable = False)
    bio = db.Column(db.String(512), nullable = True)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    portion = db.Column(db.Integer, nullable = True)
    total_time_needed = db.Column(db.Integer, nullable = True)


class RecipeStep(db.Model):
    __tablename__ = 'recipe_steps'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key = True)
    step_number = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(1024), primary_key = True)
    time_needed = db.Column(db.Integer, nullable = True)
