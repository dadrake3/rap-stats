
import boto3
import botocore
import sys

from zappa.async import task, get_async_response
from functools import partial, wraps
from collections import defaultdict
import random as rand

import .S3Helpers as s3




@s3.exp_backoff_with_jitter(exception=s3.client_error)
def zappa_get_async_response(code):
	return get_async_response(code)['response']


# needs to add @task wrapper from zappa
# needs to apply .response_id to the output
# 
def zappa_async(func):
	print('fuck')
	@task(capture_response=True)
	@wraps(func)
	def func_wrap_async(*args, **kwargs):
		return func(*args, **kwargs).response_id

	return func_wrap_async

def zappa_get_args_from_response_code(func):
	@wraps(func)
	def func_wrap(*response_codes, **kwargs):
		args = [zappa_get_async_response(code) for code in response_codes]
		return func(*args, **kwargs).response_id

	return func_wrap

def zappa_async_join(response_codes, wait_time=2):
		ready = defaultdict(lambda : False)

		while True:
		    for code in response_codes:
		        if ready[code]:
		            continue

		        response = zappa_get_async_response(code)

		        if response is not None and response['status'] == 'complete':
		            ready[code] = True

		    if len(ready) == len(response_codes):
		    	break 

		    time.sleep(wait_time)



class MapReduce:
	def __init__(self, map_func, reduce_func, reduce_mode='pair'):
		self.response_codes = []

		self.__map_func = lambda: None# lambda args: list(map(zappa_async(map_func), args))
		# self.__map_func = lambda args: list(map(map_func, args))

		# @zappa_async	
		@zappa_get_args_from_response_code
		def reduce_func_async(a, b):
			return reduce_func(a, b)

		self.__reduce_func = reduce_func_async


	def __map(self, arg_list):
		self.response_codes = self.__map_func(arg_list)
		print(self.response_codes)
		# print(self.response_codes)
		zappa_async_join(self.response_codes)

	def __reduce(self):
		reduced = self.response_codes[:]

		while len(reduced) > 1:
			reducing = []
			
			if len(reduced) % 2 > 0:
				reducing.append(reduced.pop())

			while len(reduced):
				# fix this 
				# print(reduced, reducing)
				# print(reduced, reducing)
				reducing.append(self.__reduce_func(reduced.pop(), reduced.pop()))

				# return str(curr_baking)
			zappa_async_join(reducing)

			
			reduced = reducing[:]
			# print(reduced)

		self.response_codes = reduced[:]


	def __call__(self, arg_list):
		self.__map(arg_list)
		self.__reduce()

		# return self.response_codes

		responses = map(zappa_get_async_response, self.response_codes)
		self.response_codes

		for code in self.response_codes:
			s3.delete_object(f'temp/{code}.json')

		return list(responses)


	