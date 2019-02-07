import requests
from bs4 import BeautifulSoup
import json
import sys
from os import environ

sys.path.append('./')



genius_bearer = '3jz_OOtbzge3at7YILYONJ28G70EJ43pR7yL5KE9hqcDFMvegey-lgcRzvWPS23s'

if 'SERVERTYPE' in environ and environ['SERVERTYPE'] == 'AWS Lambda':
	pass

else:
    from . import Config
    genius_bearer = Config.genius_bearer



class GeniusClient:
	## GENIUS PARAMS
	base_url = 'http://api.genius.com'
	name = 'genius',
	authorize_url = 'https://api.genius.com/oauth/authorize',
	access_token_url = 'https://api.genius.com/oauth/token',
	redirect_uri = 'https://example.com'
	bearer = genius_bearer #config.genius_bearer
	headers = {
		'Authorization': 'Bearer ' + bearer
		}


	def get_artist_id(self, artist_name):
		''' get the genius artist id from their artist name'''
		url = self.base_url + '/search'
		payload = {
			'q': artist_name
			}
		data = requests.get(url, params=payload, headers=self.headers).json()


		return data['response']['hits'][0]['result']['primary_artist']['id']


	def song_url_path_generator(self, artist_id, max_page=30):
		page = 1
		while page<max_page:
			url = '{}/artists/{}/songs'.format(self.base_url, str(artist_id))
			payload = {
				'page' : str(page),
				'per_page' : '50',
				'sort' : 'popularity'
				}
			data = requests.get(url, params=payload, headers=self.headers).json()
			
			for song in data['response']['songs']:
				if int(song['primary_artist']['id']) == artist_id:
					url_data = requests.get(self.base_url + song['api_path'], headers=self.headers).json()
					# print(song['title'])
					
					yield (song['title'], url_data['response']['song']['path'])
			page+=1

	def get_lyrics_from_song_path(self, song_path):
		
		# gotta go regular html scraping... come on Genius
		page_url = 'http://genius.com' + song_path
		page = requests.get(page_url)
		html = BeautifulSoup(page.text, 'html.parser')
		# remove script tags that they put in the middle of the lyrics
		[h.extract() for h in html('script')]

		# at least Genius is nice and has a tag called 'lyrics'!
		# updated css where the lyrics are based in HTML
		lyrics = html.find('div', class_='lyrics').get_text()
		return lyrics

	def song_lyric_generator(self, artist_id, max_page=30):
		pass








