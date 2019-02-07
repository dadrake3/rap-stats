import markovify
import json
# from zappa import task


# from Genius import GeniusClient

# Genius = GeniusClient()
# artist_id = Genius.get_artist_id('young thug')
# song_generator = Genius.get_song_paths_from_artist_id(artist_id) 

# @task(capture_response=True)
def map(func):
	def func_wrap(*args, **kwargs):
		return func(*args, **kwargs)

	return func

class MarkovModel:
	def __init__(self, model_json='', corpus='', mode='build'):
		if mode == 'build':
			self.model = markovify.NewlineText(corpus)
		elif mode == 'load':
			self.model = markovify.Text.from_json(model_json)

	def build_sentence(self, n):
		return self.model.make_short_sentence(n)

	def to_json(self):
		return self.model.to_json()

	def merge_model(self, other):
		self.model = markovify.combine(models=[self.model, other.model])






# def markov_line_by_line():
# 	combined_model = None
# 	num_songs = 50
# 	for i in range(num_songs):
# 		song = next(song_generator)
# 		raw_text = Genius.get_lyrics_from_song_path(song[1])
# 		raw_text = raw_text.lower()
# 		model = markovify.NewlineText(raw_text, retain_original=False)

# 		if combined_model:
# 			combined_model = markovify.combine(models=[combined_model, model])
# 		else:
# 			combined_model = model

# 	return combined_model
