import re
import time
import json
import sys
import string
import datetime
import itertools


from flask import Flask, jsonify, request
from collections import deque
from zappa.async import task
from functools import wraps
from collections import defaultdict


#local packages 
sys.path.append('./')
from rap_stats import Genius
from rap_stats import S3Helpers as S3
from rap_stats import Markov 
from rap_stats import Responses as res
from rap_stats import MapReduce as MR


class Status:
	unavailable = 0
	pending = 1
	available = 2

app = Flask(__name__)
genius_client = Genius.GeniusClient()
res_factory = res.ResponseFactory()

#zappa task lets you start a long running process in the background as another lambda function
# @profile
def clean_text(text):
	processed_text = text.lower()
	processed_text = re.sub("[\(\[].*?[\)\]]", "", processed_text)
	processed_text = ''.join(word.strip(string.punctuation) for word in processed_text)
	return processed_text


# S3.ProvisionedThroughputExceededException




# these can be replaced partial functions probably
# to freeze the key name
def get_artist_dict_s3():
	artist_dict = S3.get_json('artist_model_dict.json')
	return defaultdict(lambda : Status.unavailable, artist_dict)


def put_artist_dict_s3(artist_dict):
	S3.put_json(dict(artist_dict), 'artist_model_dict.json')


def update_artist_dict_s3(artist_id, status):
	artist_dict = get_artist_dict_s3()
	artist_dict[artist_id] = status
	put_artist_dict_s3(artist_dict)



def build_song_model_s3(song):
	song_hash = str(hash(str(song)))
	
	raw_text = genius_client.get_lyrics_from_song_path(song[1])
	corpus = clean_text(raw_text)
	model = Markov.MarkovModel(corpus=corpus, mode='build')
	model_json = model.to_json()

	S3.put_json(model_json, f'temp/{song_hash}.json')

	return song_hash


def merge_song_models_s3(song_hash1, song_hash2):

	model1_json = S3.get_json(f'temp/{song_hash1}.json')
	model2_json = S3.get_json(f'temp/{song_hash2}.json')

	model1 = Markov.MarkovModel(model1_json, mode='load')
	model2 = Markov.MarkovModel(model2_json, mode='load')

	model1.merge_model(model2)
	model_json = model1.to_json()
	S3.put_json(model_json, f'temp/{song_hash1}.json')
	S3.delete_object(f'temp/{song_hash2}.json')

	return song_hash1	

	        	
@task
def build_artist(artist_id=20503, num_songs=50):
	song_generator = genius_client.song_url_path_generator(artist_id) 
	songs = itertools.islice(song_generator, num_songs)

	# songs = [i for i in range(8)]
	map_func = build_song_model_s3
	reduce_func = merge_song_models_s3
	
	# map_func = lambda a : a + 1
	# reduce_func = lambda a, b : a * b

	print('starting')
	builder = MR.MapReduce(map_func, reduce_func)
	model = builder(songs)[0]
	# model = builder(songs)

	# print(model)

	S3.put_json(model, f'markov/{artist_id}.json')
	
	update_artist_dict_s3(artist_id, Status.available)



def verify_artist(func):
	def func_wrap():
		artist_status = get_artist_dict_s3()

		artist_id = request.args.get('artist_id')
		num_songs = request.args.get('num_songs')

		if not artist_id:
			return res_factory('invalid artist_id', status='error', code='404')

		else:
			if artist_status[artist_id] == Status.unavailable:

				artist_status[artist_id] = Status.pending
				S3.put_json(dict(artist_status), 'artist_model_dict.json')

				if num_songs:
					build_artist(int(artist_id), num_songs=int(num_songs))
				else:
					build_artist(int(artist_id))

				# print('heehe')
				return res_factory('artist not ready', status='Server Error', code=503)

			elif artist_status[artist_id] == Status.pending:
				return res_factory('artist not ready', status='Server Error', code=503)

			else:
				return res_factory(func())

	return func_wrap
	

@app.route('/Markov', methods=['GET'])
@verify_artist
def get_markov_lyric():
	#this is guarenteed by the wrapper
	artist_id = request.args.get('artist_id')
	model_json = S3.get_json(f'markov/{artist_id}.json')
	model = Markov.MarkovModel(model_json=model_json, mode='load')

	return model.build_sentence(140)
	# return 'this looks good'

@app.route('/clear', methods=['GET'])
def clear_dict():
	S3.put_json({}, 'artist_model_dict.json')
	return 'dict cleared'

