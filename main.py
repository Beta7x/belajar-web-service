import os
from flask import Flask
from flask_restx import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.app_context().push()

db = SQLAlchemy(app)
ma = Marshmallow(app)

api = Api(app)

class Users(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid4())
    first_name = db.Column(db.String(10))
    last_name = db.Column(db.String(20))
    username = db.Column(db.String(10), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    
    def __init__(self, first_name, last_name, username, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class UserSchema(ma.Schema):
    class Meta:
        model = Users
        load_instance = True
        sqla_session = db.session
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

new_user_params = reqparse.RequestParser()
new_user_params.add_argument('first_name', type=str, help='Your first name', location='json', required=True)
new_user_params.add_argument('last_name', type=str, help='Your last name', location='json', required=True)
new_user_params.add_argument('username', type=str, help='Your username for login', location='json', required=True)
new_user_params.add_argument('email', type=str, help='Your email', location='json', required=True)
new_user_params.add_argument('password', type=str, help='Your secure password', location='json', required=True)

@api.route('/signup')
class User(Resource):
    @api.expect(new_user_params)
    def post(self):
        args = new_user_params.parse_args()
        first_name = args['first_name']
        last_name = args['last_name']
        username = args['username']
        email = args['email']
        password = args['password']
        
        new_user = Users(first_name, last_name, username, email, password)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        user = user_schema.dump(new_user)
        
        return {
            'message': 'Successfully create new user!',
        }, 201
        
if __name__ == '__main__':
    app.run(
        host=str(os.environ.get("HOST")),
        port=os.environ.get("PORT"),
        debug=os.environ.get("DEBUG"))