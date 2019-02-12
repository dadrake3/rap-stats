
from collections import defaultdict
from functools import partial, wraps
from zappa.async import task, get_async_response
from . import S3Helpers as s3
import time

from flask import Flask, make_response, abort, url_for, redirect, request, jsonify
from . import app


# uncomment this for exponential jitter for database retries 
get_async_response = s3.exp_backoff_with_jitter(exception=s3.client_error)(get_async_response)


class InvalidResponseID(Exception):
	pass


def get_zappa_async_responses(res_id_list, delay=2):
	print(res_id_list)

	# @s3.exp_backoff_with_jitter(exception=s3.client_error)
	# jitter this function instead of doing static delay
	def get_zappa_async_responses_wrap(res_id, delay):
		while 1:
			response = get_async_response(res_id)
			if response is None:
				# raise InvalidResponseID
				continue

			# abort(404)

			if response['status'] == 'complete':
				return response['response']

		time.sleep(delay)

	zappa_async_response_mapper = lambda res_id : get_zappa_async_responses_wrap(res_id, delay)

	return list(map(zappa_async_response_mapper, res_id_list))



def zappa_async(func):
	func_wrap_async = task(func, capture_response=True)
	return lambda *args, **kwargs: func_wrap_async(*args, **kwargs).response_id
	




