import jwt
from jwt import ExpiredSignatureError
from validate_email_address import validate_email
from src import db
from src.models import User, Post, Thread_, Branch
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, reqparse


class Users(Resource):

	def get(self, user_id):
		get_all = request.args.get('getall', default=None)
		if get_all:
			users = User.query.all()
			return [x.to_dict(all_info=True) for x in users]

		#end_point = request.path.split('/')[1:]
		headers = request.headers
		args = request.args
		additional_opt = args.get("additional", [])
		if str.isdigit(user_id):
			user = User.get_user_by_id(user_id)
		else:
			user = User.get_user_by_nick(user_id)
		threads, branches, posts = None, None, None

		if "threads" in additional_opt:
			threads = [x.to_dict() for x in db.session.query(Thread_).filter_by(creator_id=user.user_id).all()]
		if "threads" in additional_opt:
			branches = [x.to_dict() for x in db.session.query(Branch).filter_by(creator_id=user.user_id).all()]
		if "threads" in additional_opt:
			posts = [x.to_dict() for x in db.session.query(Post).filter_by(creator_id=user.user_id).all()]

			user_dcit = user.to_dict(threads=threads, branches=branches, posts=posts)

			return user_dcit, 200
		return user.to_dict(), 200



	def post(self):
		end_point = request.url_rule.rule
		#print(end_point)
		if end_point == "/login":
			return self.logging()
		elif end_point == "/register":
			return self.registration()
		else:
			return {"error": "error"}, 400

	def logging(self):

		parser = reqparse.RequestParser()
		parser.add_argument('password', type=str, help='user password')
		parser.add_argument('email', type=str, help='user e-mail', required=False)
		parser.add_argument('name', type=str, help='user name', required=False)

		args = parser.parse_args()

		email = args.get("email")
		login = args.get("name")
		password = args["password"]

		if email:
			if not validate_email(email):
				return {"Error": "Invalid email format"}, 400
			user = db.session.query(User).filter_by(email=email).first()
		elif login:
			user = db.session.query(User).filter_by(nickname=login).first()
		else:
			return {"Error": "Login or email not sent"}, 400
		if not user:
			return {"Error": f"User [{login or email}] not exist "}, 400
		access = user.password_check(password)

		if not access:
			return {"error": "Incorrect password"}, 401

		user_dict = user.to_dict()
		return user_dict, 200

	def registration(self):

		parser = reqparse.RequestParser()
		parser.add_argument('name', type=str, help='user name')
		parser.add_argument('email', type=str, help='user e-mail')
		parser.add_argument('password', type=str, help='user password')

		args = parser.parse_args()
		login = args["name"]
		password = args["password"]

		email = args["email"]
		#print(login, password)

		try:
			user = User(
				nick=login,
				password=password,
				email=email
			)
			db.session.add(user)
			print(user.user_id)
			db.session.commit()

		except ValueError as ex:
			return {"Msg": "Invalid data", "Error": str(ex)}, 400
		except IntegrityError:
			return {"error": "This name is taken"}, 401

		user_dict = user.to_dict()

		return user_dict, 201


	def patch(self, user_id):

		headers = request.headers

		parser = reqparse.RequestParser()
		parser.add_argument('email', type=str, help="user's e-mail", required=False)
		parser.add_argument('name', type=str, help="user's name", required=False)
		parser.add_argument('password', type=str, help="user's password", required=False)
		parser.add_argument('access_lvl', type=int, help="user's access level", required=False)
		args = parser.parse_args()
		if user_id:
			# if token_data["access_lvl"] < 2:
			# 	return {"Error": "Insufficient rights"}, 400
			new_access_lvl = args["access_lvl"]
			if isinstance(user_id, int):
				user_to_change = User.get_user_by_id(user_id)
			else:
				user_to_change = User.get_user_by_nick(user_id)

			if not user_to_change:
				return {"Error": f"User [{user_id}] not found"}, 400
			user_to_change.access_level = new_access_lvl
			db.session.commit()

			return {"msg": "ok"}, 200
		return {"Error": "error"}, 400




