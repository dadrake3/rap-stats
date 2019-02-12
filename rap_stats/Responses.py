
import json 

class ResponseFactory():
	def __call__(self, data, status='success', code=200):
		return json.dumps({ 'status' : status, 'code' : code, 'data' : data})
		


