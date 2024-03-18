from flask_restful import Resource, reqparse
from flask import request
from src import db
from src.models import Branch, Thread_, User


class Threads(Resource):

	def get(self, thread_id=None):
		offset = request.args.get('offset', default=None, type=int)
		get_all = request.args.get('getall', default=None)
		if get_all:
			threads = Thread_.query.all()
			print(len(threads))
			return [x.to_dict() for x in threads]

		if thread_id is None or thread_id == -1:
			if isinstance(offset, int) and offset > 0:
				query = db.session.query(Thread_).order_by(Thread_.thread_id).offset(offset).limit(30)
				# print(query.statement)
				threads = query.all()
				return [t.to_dict() for t in threads], 200
			threads = db.session.query(Thread_).order_by(Thread_.thread_id).offset(0).limit(30).all()
			return [t.to_dict() for t in threads], 200
		try:
			thread_id = int(thread_id)
		except ValueError:
			return {"error": "Bad request"}, 400
		thread = db.session.query(Thread_).filter_by(thread_id=thread_id).first()
		if not thread:
			return {"error": "Thread not exist"}, 401
		thread_dict = thread.to_dict()
		if thread.branch_count == 0:
			return thread_dict, 200
		branches = thread.get_branches()
		thread_dict["branches"] = [branch.to_dict() for branch in branches]
		return thread_dict, 200

	def post(self, thread_id=None):

		if thread_id is None:
			return self.post_thread()
		return self.post_branch(thread_id)

	def post_thread(self):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument('thread_name', type=str, required=False)

		args = parser.parse_args()

		user_id = args.get("user_id")
		thread_name = args.get("thread_name")

		if user_id < 1:
			return {"error": "Auth error"}, 401
		if len(thread_name) < 5:
			return {"Error": "Thread name must be longer than five characters"}, 400
		user = db.session.query(User).filter_by(user_id=user_id).first()

		if user.access_level < 1:
			return {"Error": "Not enough rights"}, 402

		new_thread = Thread_(creator=user_id, name=thread_name)
		db.session.add(new_thread)
		db.session.commit()
		return new_thread.to_dict(), 201

	def post_branch(self, thread_id):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument('branch_name', type=str, help='branch_name is name of new branch', required=True)

		args = parser.parse_args()

		user_id = args.get("user_id")
		branch_name = args.get("branch_name")
		if user_id < 1:
			return {"Error": "Auth error"}, 401
		if len(branch_name) < 5:
			return {"Error": "Branch name must be longer than five characters"}, 400
		thread = db.session.query(Thread_).filter_by(thread_id=int(thread_id)).first()
		if not thread:
			return {"error": "Thread not exist"}, 404
		try:
			new_branch = Branch(
				thread_id=thread_id,
				name=branch_name,
				creator=user_id,

			)
			db.session.add(new_branch)
			db.session.commit()
			return new_branch.to_dict(True), 201
		except Exception as ex:
			print(ex)
			return {"Error": "Not valid data"}, 400

	def patch(self, thread_id):
		if not thread_id:
			return {"Error": "thread_id is unique id of thread being modified"}, 400
		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument("thread_id", type=str, help="thread_id is unique id of thread being modified", required=False)
		parser.add_argument("thread_name", type=str, required=False)

		args = parser.parse_args()
		user_id = args.get("user_id")

		thread_name = args.get("thread_name")
		if user_id < 1:
			return {"Error": "Auth error"}, 401
		if len(thread_name) < 5:
			return {"Error": "Thread name must be longer than five characters"}, 400
		thread = db.session.query(Thread_).filter_by(thread_id=thread_id).first()
		if not thread:
			return {"error": "Thread not exist"}, 404
		if thread_name and thread.name != thread_name:
			thread.name = thread_name
			db.session.commit()
			return thread.to_dict(), 200
		return {"Message": "No changes were made to the resource"}, 200

	def delete(self, thread_id):
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
		thread = db.session.query(Thread_).filter_by(id=int(thread_id)).first()
		if not thread:
			return {"Error": "Thread not found"}, 404
		if user.user_id != thread.creator_id and user.access_level < 3:
			return {"Error": "Not enough rights"}, 402
		if thread.branch_count > 0:
			branches = thread.get_branches(all_branches=True)
			for branch in branches:
				db.session.delete(branch)
		db.session.delete(thread)
		db.session.commit()
		return {"Message": "Delete complete"}, 204

