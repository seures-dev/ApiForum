from flask_restful import Resource, reqparse, request
from src import db
from src.models import Post, User


class Posts(Resource):

	def get(self, post_id: int, branch_id=None):

		get_count = request.args.get('get_count', default=None)
		if get_count:
			count = Post.query.count()
			return {"post_count": count, "chunk_size": 2000}, 200
		get_all = request.args.get('getall', default=0, type=int)
		if get_all:  # returns by list[post*2000]
			get_all_int = int(get_all)
			branches = Post.query.order_by(Post.u_id).offset(get_all_int * 2000).limit(2000).all()
			return [x.to_dict() for x in branches], 200

		if branch_id is None:
			post = Post.query.filter_by(u_id=post_id).first()
		else:
			post = Post.query.filter_by(branch_id=branch_id, into_branch_id=post_id).first()

		if not post:
			return {"Error": "Post doesn't exist"}, 400
		return post.to_dict(), 200

	def patch(self, post_id, branch_id=None):

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

		if branch_id is None:
			post = Post.query.filter_by(u_id=post_id).first()
		else:
			post = Post.query.filter_by(branch_id=branch_id, into_branch_id=post_id).first()


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

	def delete(self, post_id, branch_id=None):
		if branch_id is None:
			post = Post.query.filter_by(u_id=post_id).first()
		else:
			post = Post.query.filter_by(branch_id=branch_id, into_branch_id=post_id).first()

		if not post:
			return {"Messagef": "Post doesn't exist"}, 404
		db.session.delete(post)
		db.session.commit()
		return {"Message": "Delete successfully"}, 204



