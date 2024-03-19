from flask_restful import Resource, reqparse
from flask import request
from src import db
from src.models import Branch, Thread_, User
from src.services.thread_service import ThreadService

class Threads(Resource):

	def get(self, thread_id: int | None = None):

		offset = request.args.get('offset', default=0, type=int)
		get_all = request.args.get('getall', default=None)
		if offset < 0:
			offset = 0
		else:
			offset = (offset // 30) * 30
		print(offset)
		if get_all:
			return ThreadService.get_all_threads()

		if thread_id is None:
			return ThreadService.get_treads_with_offset(offset)

		return ThreadService.get_thread_by_id(thread_id, offset)

	def post(self, thread_id: int | None = None):

		if thread_id is None:
			return self.post_thread()
		return self.post_branch(thread_id)

	def post_thread(self):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument('thread_name', type=str, required=False)

		return ThreadService.post_thread(parser)

	def post_branch(self, thread_id: int):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument('branch_name', type=str, help='branch_name is name of new branch', required=True)
		return ThreadService.post_branch(thread_id, parser)


	def patch(self, thread_id: int):
		if not thread_id:
			return {"Error": "thread_id is unique id of thread being modified"}, 400
		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument("thread_id", type=str, help="thread_id is unique id of thread being modified", required=False)
		parser.add_argument("thread_name", type=str, required=False)
		return ThreadService.patch_thread(thread_id, parser)

	def delete(self, thread_id: int):
		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		return ThreadService.delete_thread(thread_id, parser)

