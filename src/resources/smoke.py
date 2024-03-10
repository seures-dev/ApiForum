from flask_restful import Resource


class Smoke(Resource):

	def get(self):
		return {"message": "Ok"}, 200
	pass