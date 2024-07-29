from flask_restful import Resource, reqparse
from models import User, Post
from schemas import user_schema, post_schema, users_schema, posts_schema
from config import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


post_parser = reqparse.RequestParser()
user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
post_parser.add_argument('title', type=str, required=True, help="Title is required")
post_parser.add_argument('content', type=str, required=True, help="Content is required")

class UserRegister(Resource):
    def post(self):
        data = user_parser.parse_args()
        if User.query.filter_by(username=data['username']).first():
            return {"message": "User already exists"}, 400
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully"}, 201

class UserLogin(Resource):
    def post(self):
        data = user_parser.parse_args()
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200
        return {"message": "Invalid credentials"}, 401

class PostResource(Resource):
    @jwt_required()
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return post_schema.dump(post), 200

    @jwt_required()
    def delete(self, post_id):
        user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        if post.author.id != user_id:
            return {"message": "Permission denied"}, 403
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post deleted"}, 200

    @jwt_required()
    def put(self, post_id):
        data = post_parser.parse_args()
        post = Post.query.get_or_404(post_id)
        user_id = get_jwt_identity()
        if post.author.id != user_id:
            return {"message": "Permission denied"}, 403
        post.title = data['title']
        post.content = data['content']
        db.session.commit()
        return post_schema.dump(post), 200

class PostListResource(Resource):
    def get(self):
        posts = Post.query.all()
        return posts_schema.dump(posts), 200

    @jwt_required()
    def post(self):
        data = post_parser.parse_args()
        user_id = get_jwt_identity()
        new_post = Post(title=data['title'], content=data['content'], user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return post_schema.dump(new_post), 201
