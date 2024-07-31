from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Post

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
