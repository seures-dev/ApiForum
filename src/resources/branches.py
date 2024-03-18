from flask_restful import Resource, reqparse, request
from src.services.branch_service import BranchService


class Branches(Resource):

    def get(self, branch_id: int | None = None) -> tuple[dict, int] | tuple[list[dict], int]:
        get_all = request.args.get('getall', default=None)
        if get_all:
            branches: tuple[list[dict], int] = BranchService.get_all_branches()
            return branches
        if branch_id is None or not isinstance(branch_id, int):
            return {"Error": "Branch id doesn't specified"}, 400
        offset = request.args.get('offset', type=int, default=0)
        offset = (offset // 30) * 30

        branch: tuple[dict, int] = BranchService.get_branch(branch_id, offset)
        return branch

    def post(self, branch_id: int) -> tuple[dict, int]:
        """
        :param branch_id: branch where will create the post:
        :return: tuple[dict, int]
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
                            required=True)
        parser.add_argument("content", type=str, help="post content is some string message", required=True)

        args = parser.parse_args()
        user_id = args.get("user_id")
        content = args.get("content")
        return BranchService.post_message(branch_id, user_id, content)

    def patch(self, branch_id: int) -> tuple[dict, int]:
        """
        :param branch_id: branch which patching:
        :return: tuple[dict, int]
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
                            required=True)
        parser.add_argument("branch_name", type=str, required=False)
        return BranchService.patch_branch(branch_id, parser)

    def delete(self, branch_id: int) -> tuple[dict, int]:
        """
        :param branch_id: branch which deleting, also delete post which were in branch:
        :return: tuple[dict, int]
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", type=int, help="user_id — number, which is the user's unique identifier",
                            required=True)
        return BranchService.delete_branch(branch_id, parser)
