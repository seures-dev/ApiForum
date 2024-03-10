from flask_restful import Resource, reqparse, request
from src import db
from src.models import Branch, Post, User
from src.different import time_tracker


class Branches(Resource):


	def get(self, branch_id=None, offset=0):
		get_all = request.args.get('getall', default=None)
		if get_all:
			branches = Branch.query.all()
			return [x.to_dict() for x in branches]
		if not branch_id:
			branches = db.session.query(Branch).order_by(Branch.id).limit(30).all()
			return [x.to_dict() for x in branches], 200

		branch = db.session.query(Branch).filter_by(id=int(branch_id)).first()
		if not branch:
			return {"Error": "Branch doesn't exist"}, 400

		if branch.message_count == 0:
			return branch.to_dict(), 200
		branch_dict = branch.to_dict()
		posts = branch.get_posts()
		branch_dict["posts"] = [p.to_dict() for p in posts]
		return branch_dict, 200

	def post(self, branch_id, page=1):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument("content", type=str, help="post content is some string message", required=True)

		args = parser.parse_args()
		user_id = args.get("user_id")
		content = args.get("content")

		if user_id < 1:
			return {"Error": "auth error"}, 401
		if len(content) < 2:
			return {"Error": "message length must be longer than two characters"}, 400
		branch = db.session.query(Branch).filter_by(id=int(branch_id)).first()
		if not branch:
			return {"Error": "Branch not found"}, 404
		into_branch_ids = db.session.query(Post.into_branch_id).filter_by(branch_id=branch_id).all()
		into_branch_id = max(item[0] for item in into_branch_ids) + 1

		try:
			post = Post(
				b_id=branch.id,
				u_id=1,
				ib_id=into_branch_id,
				content=content,
				creator=user_id
			            )
			db.session.add(post)
			db.session.commit()
			branch_dict = branch.to_dict()
			posts = branch.get_posts()
			branch_dict["posts"] = [p.to_dict() for p in posts]
			return branch_dict, 201

		except (KeyError, ValueError) as ex:
			return {"Error": ex}, 400

	def patch(self, branch_id):
		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument("branch_name", type=str, required=False)

		args = parser.parse_args()
		user_id = args.get("user_id")
		branch_name = args.get("branch_name")
		if user_id < 1:
			return {"Error": "Auth error"}, 401
		branch = db.session.query(Branch).filter_by(id=int(branch_id)).first()
		if not branch:
			return {"Error": "Branch not found"}, 402
		if branch_name:
			branch.name = branch_name
			db.session.commit()
			if branch.message_count == 0:
				return branch.to_dict(), 200
			branch_dict = branch.to_dict()
			posts = branch.get_posts()
			branch_dict["posts"] = [p.to_dict() for p in posts]
			return branch_dict, 200
		return {"Error": "No changes were made to the resource"}, 200

	def delete(self, branch_id):
		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		args = parser.parse_args()
		user_id = args.get("user_id")
		if user_id < 1:
			return {"Error": "Auth error"}, 401
		user = db.session.query(User).filter_by(user_id=user_id).first()
		if not user:
			return {"Error": "Unknown user"}, 401
		branch = db.session.query(Branch).filter_by(id=int(branch_id)).first()
		if not branch:
			return {"Error": "Branch not found"}, 402
		if user.user_id != branch.creator_id and user.access_level < 3:
			return {"Error": "Not enough rights"}, 402
		if branch.message_count > 0:
			posts = branch.get_posts(all_post=True)
			for post in posts:
				db.session.delete(post)
		db.session.delete(branch)
		db.session.commit()
		return {"Message": "Delete complete"}, 204
