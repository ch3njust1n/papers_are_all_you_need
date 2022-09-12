'''
'''
import sys
import datetime
import json
from json.decoder import JSONDecodeError
import urllib.request
from urllib.error import URLError, HTTPError
from multiprocessing import Manager
from threading import Thread
from papers import utils

from tqdm import tqdm
from bs4 import BeautifulSoup
from colorama import Fore, Style


class Conference(object):
	def __init__(self, name, year):
		
		self.name = name
		self.year = str(year)
		self.conf = {
			'neurips': 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/neurips',
			'icml': 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/icml',
			'aistats': 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/aistats',
			'iclr': '',
			'cvpr': '',
			'emnlp': '',
			'aaai': '',
			'sysml': '',
			'naacl': '',
			'icme': '',
			'chil': '',
			'icip': '',
			'ijcai': '',
			'acl': '',
			'sigir': '',
			'iccv': '',
			'eccv': ''
		}
		self.repo = self.conf[name]

	'''
	Get meta data of accepted papers from pseudo-api

	outputs:
	data (list) List of dicts of paper meta data
	'''
	def accepted_papers(self):

		url = '/'.join([self.repo, f'{self.name}_{self.year}.json'])
		with urllib.request.urlopen(url) as file:
			return json.loads(file.read().decode())


	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	inputs:
	papers 		   (list) 			List of dicts of papers
	title_kw       (list, optional) Keywords to match in title
	author_kw      (list, optional) Names to match in authors list
	affiliation_kw (list, optional) Names to match in affiliation list

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def query_papers(self, papers, title_kw=None, author_kw=None, affiliation_kw=None):

		extracted = []

		if title_kw: title_kw = [w.lower() for w in title_kw if len(w) > 0]
		if author_kw: author_kw = [w.lower() for w in author_kw if len(w) > 0]
		if affiliation_kw: affiliation_kw = [w.lower() for w in affiliation_kw if len(w) > 0]

		has_title = lambda words, title: any(word in title.lower() for word in words)
		has_author = lambda names, authors: any(n in authors.lower() for n in names)
		has_affiliation = lambda aff, authors: any(a in authors.lower() for a in aff)

		for p in papers:
			title = p['title']
			try:
				authors = [' '.join([' '.join(a['given_name']), a['family_name']]) for a in p['authors']]
				affiliations = [a['institution'] for a in p['authors']]
			except:
				print(p)
				sys.exit()


			if (title_kw and has_title(title_kw, title)) or (author_kw and has_author(author_kw, authors)) or\
				(affiliation_kw and has_affiliation(affiliation_kw, affiliations)):
				extracted.append({'title': title, 'authors': authors, 'affiliations': affiliations, 'award': p['award'],
					'hash': p['hash'], 'url': p['url']})

		return extracted