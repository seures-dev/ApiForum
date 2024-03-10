from flask_restful import Resource, reqparse, request
from src import db
from src.models import Post, User


class Posts(Resource):

	def get(self, post_id, branch_id):

		get_count = request.args.get('get_count', default=None)
		if get_count:
			count = count = Post.query.count()
			return {"post_count": count,"chunk_size": 2000}, 200
		get_all = request.args.get('getall', default=None)
		if get_all:
			get_all_int = int(get_all)
			branches = Post.query.order_by(Post.u_id).offset(get_all_int * 2000).limit(2000).all()
			return [x.to_dict() for x in branches]
		post = db.session.query(Post).filter_by(branch_id=branch_id, into_branch_id=post_id).first()
		if not post:
			return {"Error": "Post doesn't exist"}
		return post.to_dict()

	def patch(self, post_id, branch_id):

		parser = reqparse.RequestParser()
		parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
		                    required=True)
		parser.add_argument("content", type=str, help="new content off the post", required=True)
		args = parser.args
		user_id = args.get("user_id")
		content = args.get("content")

		if user_id < 1:
			return {"Error": "Auth error"}, 401

		user = db.session.query(User).filter_by(user_id=user_id).first()

		if not user:
			return {"Error": "Unknown user"}, 401

		post = db.session.query(Post).filter_by(branch_id=branch_id, into_branch_id=post_id).first()

		if user.user_id != post.creator_id and user.access_level < 2:
			return {"Error": "Not enough rights"}, 402

		if not post:
			return {"Error": "Post doesn't exist"}, 404

		if content:
			post.content = content
			db.session.add(post)
			db.session.commit()
			return {"Message": "Updated successfully"}, 200
		return {"Message": "No changes were made to the resource"}, 200

	def delete(self, branch_id, post_id):
		post = db.session.query(Post).filter_by(branch_id=branch_id, into_branch_id=post_id).first()
		if not post:
			return {"Messagef": "Post doesn't exist"}, 404
		db.session.delete(post)
		db.session.commit()
		return {"Message": "Updated successfully"}, 204



