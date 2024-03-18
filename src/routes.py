
from src.resources.posts import Posts
from src.resources.branches import Branches
from src.resources.smoke import Smoke
from src.resources.threads import Threads
from src.resources.users import Users
from src import api


api.add_resource(Smoke, "/smoke", strict_slashes=False)
api.add_resource(Posts,  "/posts/<int:post_id>/<int:branch_id>", strict_slashes=False)
api.add_resource(Branches, "/branches", "/branches/<int:branch_id>/")
api.add_resource(Threads,  "/threads", "/threads/<int:thread_id>", strict_slashes=False)
api.add_resource(Users, "/login", "/register", "/users/<user_id>", strict_slashes=False)

