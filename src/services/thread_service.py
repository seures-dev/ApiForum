
from src.models import Branch, Thread_, User
from src import db


class ThreadService:

	@staticmethod
	def get_all_threads() -> tuple[list[dict], int]:
		threads = Thread_.query.all()
		return [x.to_dict() for x in threads], 200

	@staticmethod
	def get_treads_with_offset(offset: int) -> tuple[list[dict], int]:
		threads = Thread_.query.order_by(Thread_.thread_id).offset(offset).limit(30).all()

		return [t.to_dict() for t in threads], 200

	@staticmethod
	def get_thread_by_id(thread_id: int, offset: int) -> tuple[dict, int]:
		thread = db.session.query(Thread_).filter_by(thread_id=thread_id).first()
		if not thread:
			return {"error": "Thread not exist"}, 401
		thread_dict = thread.to_dict()
		if thread.branch_count == 0:
			return thread_dict, 200
		branches = thread.get_branches(offset)
		thread_dict["branches"] = [branch.to_dict() for branch in branches]
		return thread_dict, 200

	@staticmethod
	def post_thread(parser) -> tuple[dict, int]:
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

	@staticmethod
	def post_branch(thread_id: int, parser) -> tuple[dict, int]:
		args = parser.parse_args()

		user_id = args.get("user_id")
		branch_name = args.get("branch_name")
		if user_id < 1:
			return {"Error": "Auth error"}, 401
		if len(branch_name) < 5:
			return {"Error": "Branch name must be longer than five characters"}, 400
		thread = Thread_.query.filter_by(thread_id=int(thread_id)).first()
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
			return new_branch.to_dict(), 201
		except Exception as ex:
			print(ex)
			return {"Error": f"Not valid data \n {str(ex)}"}, 400


	@staticmethod
	def patch_thread(thread_id: int, parser) -> tuple[dict, int]:

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


	@staticmethod
	def delete_thread(thread_id: int, parser) -> tuple[dict, int]:
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
