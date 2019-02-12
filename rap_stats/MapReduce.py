
import boto3
import botocore
import sys

from collections import defaultdict
import random as rand

from . import ZappaHelpers as zap

#add use s3 option to either store temps in s3 or to store temps in dynamo db
#small values use dynamo 

# add different async methods i.e. parallell log reduction,
# or dont load everything into memory and just iterate straight through

# add options for it to be serial or asyncronous 

# add options for different reduction widths, i.e. how many args the merge function takes
# this is complex but it will be ok 
# zip it all together and just split at the trailing ungrouped items

# build factory functions for generating the map and reduce functions


class MapReduce:
	def __init__(self, map_func, reduce_func, reduce_mode='pair'):
		# self.response_codes = []
		self.__responses = []
		self.__map_func = zap.zappa_async(map_func)
		self.__reduce_func = zap.zappa_async(reduce_func)


	def __map(self, arg_list):
		response_codes = list(map(self.__map_func, arg_list))
		self.__responses = zap.get_zappa_async_responses(response_codes)


	def __reduce(self):

		responses = self.__responses[:]

		while len(responses) > 1:
			print('__reduce', responses)
			response_ids = []
			
			carry = []
			if len(responses) % 2 > 0:
				carry.append(responses.pop())

			n = len(responses)
			arg_pairs = zip(responses[:n//2], responses[n//2:])
			response_ids = map(lambda arg : self.__reduce_func(arg[0], arg[1]), arg_pairs)

			responses = zap.get_zappa_async_responses(response_ids) + carry 

		self.__responses = responses[:]



	def __call__(self, arg_list):
		self.__map(arg_list)
		self.__reduce()

		# return self.responses[0]
		return self.__responses[0]



# class MapReduce:
# 	def __init__(self, map_func, reduce_func, reduce_mode='pair'):
# 		# self.response_codes = []
# 		self.responses = []
# 		self.__map = None

		
		
# 		# self.__reduce_func = zap.zappa_async(reduce_func)


# 	def __map(self, arg_list):
# 		response_codes = list(map(self.__map_func, arg_list))
# 		self.responses = zap.get_zappa_async_responses(response_codes)

# 		print(responses)



# 	def __map_factory(self, map_func):
# 		async_map_func = zap.zappa_async(map_func)

# 		def __map(self, arg_list):
# 			response_codes = list(map(async_map_func, arg_list))
# 			self.responses = zap.get_zappa_async_responses(response_codes)

# 			print(responses)


# 		self.__map = __map




	