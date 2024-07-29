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
        """
        Register a new user
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  description: The user's username.
                password:
                  type: string
                  description: The user's password.
        responses:
          201:
            description: User created successfully
          400:
            description: User already exists
        """
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
        """
        User login
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  description: The user's username.
                password:
                  type: string
                  description: The user's password.
        responses:
          200:
            description: Login successful
          401:
            description: Invalid credentials
        """
        data = user_parser.parse_args()
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200
        return {"message": "Invalid credentials"}, 401

class PostResource(Resource):
    @jwt_required()
    def get(self, post_id):
        """
        Get a specific post
        ---
        tags:
          - Posts
        parameters:
          - in: path
            name: post_id
            type: integer
            required: true
            description: ID of the post to retrieve
        responses:
          200:
            description: Post retrieved successfully
          404:
            description: Post not found
        """
        post = Post.query.get_or_404(post_id)
        return post_schema.dump(post), 200

    @jwt_required()
    def delete(self, post_id):
        """
        Delete a post
        ---
        tags:
          - Posts
        parameters:
          - in: path
            name: post_id
            type: integer
            required: true
            description: ID of the post to delete
        responses:
          200:
            description: Post deleted successfully
          403:
            description: Permission denied
          404:
            description: Post not found
        """
        user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        if post.author.id != user_id:
            return {"message": "Permission denied"}, 403
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post deleted"}, 200

    @jwt_required()
    def put(self, post_id):
        """
        Update a post
        ---
        tags:
          - Posts
        parameters:
          - in: path
            name: post_id
            type: integer
            required: true
            description: ID of the post to update
          - in: body
            name: body
            schema:
              type: object
              required:
                - title
                - content
              properties:
                title:
                  type: string
                  description: The title of the post.
                content:
                  type: string
                  description: The content of the post.
        responses:
          200:
            description: Post updated successfully
          403:
            description: Permission denied
          404:
            description: Post not found
        """
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
        """
        Get all posts
        ---
        tags:
          - Posts
        responses:
          200:
            description: A list of posts
            schema:
              type: array
              items:
                $ref: '#/definitions/Post'
        """
        posts = Post.query.all()
        return posts_schema.dump(posts), 200

    @jwt_required()
    def post(self):
        """
        Create a new post
        ---
        tags:
          - Posts
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - title
                - content
              properties:
                title:
                  type: string
                  description: The title of the post.
                content:
                  type: string
                  description: The content of the post.
        responses:
          201:
            description: Post created successfully
        """
        data = post_parser.parse_args()
        user_id = get_jwt_identity()
        new_post = Post(title=data['title'], content=data['content'], user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return post_schema.dump(new_post), 201
