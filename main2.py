

# import re
# import time
# import json
# import sys
# import string
# import datetime


# from flask import Flask, jsonify, request
# from collections import deque
# from zappa.async import task, get_async_response
# from functools import wraps
# from collections import defaultdict

# #local packages 
# sys.path.append('./')
# from rap_stats import Genius
# from rap_stats import S3Helpers as S3
# from rap_stats import Markov 
# from rap_stats import Responses as res

# test = 0

# app = Flask(__name__)
# genius_client = Genius.GeniusClient()

# class Status:
# 	unavailable = 0
# 	pending = 1
# 	available = 2

# # def get_artist_status_dict():
# # 	# first try getting the object from s3

# # 	# else create an empty one
# # 	return defaultdict(lambda : Status.unavailable)

# #this needs to proteted from other thread via a spin lock 
# # artist_status = get_artist_status_dict()
# # artist_status_mutex = Lock()
# # print(type(artist_status_mutex))

# res_factory = res.ResponseFactory()


# # artist_status[20503] = 2
# def error_wrap(func):
# 	@wraps(func)
# 	def func_wrap(*args, **kwargs):
# 		try:
# 			return func(*args, **kwargs)
# 		except Exception as e:
# 			# print(e)
# 			return str(e)

# 	return func_wrap
# #zappa task lets you start a long running process in the background as another lambda function
# # @profile
# def clean_text(text):
# 	processed_text = text.lower()
# 	processed_text = re.sub("[\(\[].*?[\)\]]", "", processed_text)
# 	processed_text = ''.join(word.strip(string.punctuation) for word in processed_text)
# 	return processed_text


# @task(capture_response=True)
# def build_song_model(artist_id, song):
# 	# print(f'building {song_path}')
# 	song_hash = ''
# 	while 1:
# 		try:
# 			song_hash = str(hash(str(song)))
# 			break
# 		except botocore.errorfactory.ProvisionedThroughputExceededException as e:
# 			time.sleep(2)

# 	# print(f'BUILDING: {datetime.datetime.now().time()}: {artist_id}/temp/{song_hash}.json')


# 	raw_text = genius_client.get_lyrics_from_song_path(song[1])
# 	corpus = clean_text(raw_text)
# 	model = Markov.MarkovModel(corpus=corpus, mode='build')
# 	model_json = model.to_json()

# 	S3.put_json(model_json, f'{artist_id}/temp/{song_hash}.json')

# 	return song_hash
# 	# return str(corpus)

# @task(capture_response=True)
# def merge_song_models(artist_id, id1, id2):
# 	song_hash1 = song_hash2 = ''

# 	while 1:
# 		try:
# 			song_hash1 = get_async_response(id1)['response']
# 			song_hash2 = get_async_response(id2)['response']
# 			break
# 		except botocore.errorfactory.ProvisionedThroughputExceededException as e:
# 			time.sleep(2)

# 	# print(f'MERGING: {datetime.datetime.now().time()}: {artist_id}/temp/{song_hash1}.json', f'{artist_id}/temp/{song_hash2}.json')
		
# 	# get model from s3
# 	model1_json = S3.get_json(f'{artist_id}/temp/{song_hash1}.json')
# 	model2_json = S3.get_json(f'{artist_id}/temp/{song_hash2}.json')

# 	model1 = Markov.MarkovModel(model1_json, mode='load')
# 	model2 = Markov.MarkovModel(model2_json, mode='load')
# 	# print('this is the type', type(model2))
# 	# print(model2)

# 	model1.merge_model(model2)
# 	model_json = model1.to_json()
# 	S3.put_json(model_json, f'{artist_id}/temp/{song_hash1}.json')
# 	S3.delete_object(f'{artist_id}/temp/{song_hash2}.json')

# 	return song_hash1	



# def async_join(baking):
# 	baked = []#defaultdict(lambda : False)
# 	while True:
# 	    for b in baking:
# 	        # if 
# 	        if b in baked:
# 	            continue

# 	        response = get_async_response(b)
# 	        if response is not None and response['status'] == 'complete':
# 	            # baked[b] = True
# 	            baked.append(b)

# 	    if len(baked) == len(baking):
# 	    	return baked
# 	    time.sleep(2)
	        	

# @task
# # @app.route('/build')
# def build_artist(artist_id=20503, num_songs=50):
# 	# print(f'building {artist_id}')
# 	# time.sleep(60)
# 	song_generator = genius_client.song_url_path_generator(artist_id) 

# 	print(f'MAPPING {datetime.datetime.now().time()}')
# 	#map
# 	baking = []
# 	count = 0
# 	for song in song_generator:
# 	# for i in range(50):
# 		# song = next(song_generator)
# 		baking.append(build_song_model(artist_id, song).response_id)
# 		# baking.append(build_song_model(i).response_id)
# 		# baking.append(build_song_model(i))
# 		if count > num_songs:
# 			break
# 		count += 1
#     #join	
# 	print(baking)
# 	async_join(baking)
# 	baked = baking[:]
#     # reduce

# 	# 
# 	# print('reducing')
# 	# print(f'REDUCING {datetime.datetime.now().time()}')
# 	i = 1
# 	while len(baked) > 1:
# 		curr_baking = []
# 	# \		# print(baked)
			
# 		if len(baked) % 2 > 0:
# 			curr_baking.append(baked.pop())

# 		while len(baked):
# 			curr_baking.append(merge_song_models(artist_id, baked.pop(), baked.pop()).response_id)

# 			# return str(curr_baking)
# 		async_join(curr_baking)

# 		baked = curr_baking[:]

# 	model_id = get_async_response(baked[0])['response']

# 	# model_json = get_async_response(baked[0])['response']
# 	model_json = S3.get_json(f'{artist_id}/temp/{model_id}.json')

# 	S3.put_json(model_json, f'markov/{artist_id}.json')
# 	S3.delete_object(f'{artist_id}/temp/{model_id}.json')

# 	artist_status = defaultdict(lambda : Status.unavailable, S3.get_json('artist_model_dict.json'))
# 	artist_status[artist_id] = Status.available
# 	S3.put_json(dict(artist_status), 'artist_model_dict.json')







# 	# num_songs = 10
# 	# ret = []
# 	# for i in range(num_songs):
# 	# 	# song = next(song_generator)
# 	# 	ret.append(build_artist_model(i))






# 	# count = 0
# 	# # for song in song_generator:
# 	# for i in range(num_songs):






# 	# 	song = next(song_generator)
# 	# 	raw_text = genius_client.get_lyrics_from_song_path(song[1])
# 	# 	raw_text = raw_text.lower()
# 	# 	corpus += raw_text

# 	# 	if count > num_songs:
# 	# 		break
# 	# # 	# break
# 	# # # # Build the model.
# 	# model = Markov.MarkovModel(corpus=corpus, mode='build')
# 	# model_json = model.to_json()
# 	# print(model_json)
# 	# # # Save the model to s3
# 	# S3.put_json(model_json, f'markov-{artist_id}.json')

# 	# artist_status = defaultdict(lambda : Status.unavailable, S3.get_json('artist_model_dict.json'))
# 	# artist_status[artist_id] = Status.available
# 	# S3.put_json(dict(artist_status), 'artist_model_dict.json')

# 	# return str(ret)

# @app.route('/clear', methods=['GET'])
# def clear_dict():
# 	S3.put_json({}, 'artist_model_dict.json')
# 	return 'dict cleared'

# def verify_artist(func):
# 	def func_wrap():
# 		artist_id = request.args.get('artist_id')
# 		artist_status = defaultdict(lambda : Status.unavailable, S3.get_json('artist_model_dict.json')) 
# 		num_songs = request.args.get('num_songs')

# 		if not artist_id:
# 			return res_factory('invalid artist_id', status='error', code='404')

# 		else:
# 			# artist_status_mutex.aquire()

# 			if artist_status[artist_id] == Status.unavailable:

# 				artist_status[artist_id] = Status.pending
# 				S3.put_json(dict(artist_status), 'artist_model_dict.json')

# 				if num_songs:
# 				# artist_status_mutex.release()
# 					build_artist(int(artist_id), num_songs=int(num_songs))
# 				else:
# 					build_artist(int(artist_id))

# 				# print('heehe')
# 				return res_factory('artist not ready', status='Server Error', code=503)

# 			elif artist_status[artist_id] == Status.pending:
# 				# artist_status_mutex.release()
# 				return res_factory('artist not ready', status='Server Error', code=503)

# 			else:
# 				# artist_status_mutex.release()
# 				return res_factory(func())

# 	return func_wrap


# @app.route('/Markov', methods=['GET'])
# # @error_wrap
# @verify_artist
# def get_markov_lyric():
# 	#this is guarenteed by the wrapper
# 	artist_id = request.args.get('artist_id')
# 	model_json = S3.get_json(f'markov/{artist_id}.json')
# 	model = Markov.MarkovModel(model_json=model_json, mode='load')

# 	return model.build_sentence(140)
# 	# return 'this looks good'

# @app.route('/hello', methods=['GET'])
# def hello_world():
# 	global test
# 	# val = int(environ['A'])
# 	# val += 1
# 	# environ['A'] = str(val)
# 	# return str(environ['A'])

# 	test += 1
# 	return str(test)

# # if __name__ == '__main__':
# # 	build_artist(20503)



# def reduce():
# 	pass



























































