from src.models import Branch, Post, User, db
from sqlalchemy import asc

class BranchService:

    @staticmethod
    def _get_branch_dict_with_posts(branch: Branch, offset: int = 0) -> dict:
        branch_dict = branch.to_dict()
        posts = branch.get_posts(offset)
        if posts:
            branch_dict["posts"] = [p.to_dict() for p in posts]
        return branch_dict

    @staticmethod
    def get_branch(branch_id, offset=0) -> tuple[dict, int]:
        branch = Branch.query.filter_by(id=int(branch_id)).first()
        if not branch:
            return {"Error": "Branch doesn't exist"}, 400
        branch_dict = branch.to_dict()
        if branch.message_count < 1:
            return branch_dict, 200
        posts = branch.get_posts(offset)
        if posts:
            branch_dict["posts"] = [p.to_dict() for p in posts]
        return branch_dict, 200

    @staticmethod
    def get_all_branches() -> tuple[list[dict], int]:
        branches = Branch.query.all()
        return [x.to_dict() for x in branches], 200

    @staticmethod
    def post_message(branch_id: int, user_id: int, message: str) -> tuple[dict, int]:

        if user_id < 1:
            return {"Error": "auth error"}, 401

        if len(message) < 2:
            return {"Error": "message length must be longer than two characters"}, 400

        if not User.query.filter_by(user_id=user_id).first():
            return {"Error": "auth error"}, 401
        branch: Branch = Branch.query.filter_by(id=int(branch_id)).first()
        if not branch:
            return {"Error": "Branch not found"}, 404

        try:
            post = Post(
                b_id=branch.id,
                content=message,
                creator=user_id
            )
            db.session.add(post)
            db.session.commit()
            offset = (post.into_branch_id // 30) * 30
            branch_dict = branch.to_dict()
            if branch.message_count < 1:
                return branch_dict, 200
            posts = branch.get_posts(offset)
            if posts:
                branch_dict["posts"] = [p.to_dict() for p in posts]
            return branch_dict, 200

        except Exception as ex:
            return {"Error": ex}, 400

    @staticmethod
    def patch_branch(branch_id: int, parser) -> tuple[dict, int]:

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
        posts = branch.get_posts(0)
        if posts:
            branch_dict["posts"] = [p.to_dict() for p in posts]
        return branch_dict, 200

    @staticmethod
    def delete_branch(branch_id, parser) -> tuple[dict, int]:
        args = parser.parse_args()
        user_id = args.get("user_id")
        if user_id < 1:
            return {"Error": "Auth error"}, 401
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"Error": "Unknown user"}, 401
        branch = Branch.query.filter_by(id=int(branch_id)).first()
        if not branch:
            return {"Error": "Branch not found"}, 402
        if user.user_id != branch.creator_id and user.access_level < 3:
            return {"Error": "Not enough rights"}, 402
        if branch.message_count > 0:
            posts = branch.get_posts(all_post=True)
            for post in posts:
                db.session.delete(post)
        try:
            db.session.delete(branch)
            db.session.commit()
        except Exception as e:
            return {'Error': str(e)}, 400

        Post.query.filter_by(branch_id=branch_id).delete()
        db.session.commit()

        return {"Message": "Delete complete"}, 204
