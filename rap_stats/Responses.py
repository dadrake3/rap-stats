
class ResponseFactory():
	def __call__(self, data, status='success', code=200):

		return str({ 'status' : status, 'code' : code, 'data' : data})
		


