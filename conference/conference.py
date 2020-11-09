import json
import urllib.request
from urllib.error import URLError, HTTPError
from multiprocessing import Process, Manager, cpu_count, Value
from conference import utils

from tqdm import tqdm
from bs4 import BeautifulSoup
from colorama import Fore, Style


class NeurIPS(object):
	def __init__(self, year):
		self.year = year
		self.base = f'https://papers.nips.cc'


	'''
	outputs:
	url (str) Formatted url for conference proceedings page
	'''
	def get_url(self, year):
		return f'{self.base}/paper/{year}'


	'''
	Build a collection of the proceedings meta data

	inputs:
	proceedings (multiprocessing.Manager.list) List for collecting meta data
	errors      (multiprocessing.Manager.list) List for collecting errors
	title 		(str)						   Paper title
	url 		(str) 						   URL to paper's meta data
	'''
	def build_proceedings(self, proceedings, errors, title, url):
		try:
			resp = urllib.request.urlopen(url)
			soup = BeautifulSoup(resp.read(), 'html.parser')

			metadata_url = ''

			for a in soup.find_all('a'):
				href = a['href']
				if href.endswith('Metadata.json'): 
					metadata_url = href
					break

			with urllib.request.urlopen(''.join([self.base, metadata_url])) as file:
				data = json.loads(file.read().decode())
				hash_id = url.split('/')[-1].split('-')[0]
				url = '/'.join([self.base, 'paper', self.year, 'file', hash_id])+'-Paper.pdf'
				proceedings.append({'title': data['title'], 'authors': data['authors'], 'award': data['award'], 
					'hash': hash_id, 'url': url})
		except HTTPError as e:
			errors.append({'title':title, 'url': url})


	'''
	Replace each paper with their NeurIPS meta data.

	inputs:
	papers (list) List of dicts of papers

	outputs:
	papers (list) List of dicts of papers updated with meta data
	'''
	def get_metadata(self, papers):
		print('collecting meta data...')

		def batch(iterable, size=1):
			l = len(iterable)
			for i in range(0, l, size):
				yield iterable[i:min(i + size, l)]

		manager = Manager()
		proceedings, errors = manager.list(), manager.list()

		pbar = tqdm(total=len(papers))

		for block in batch(papers, cpu_count()):
			procs = [Process(target=self.build_proceedings, args=(proceedings, errors, p['title'], p['href'],)) for p in block]
				
			for p in procs: p.start()
			for p in procs: p.join()

			pbar.update(len(block))

		pbar.close()

		if len(errors) > 0: 
			print(f'\n{Fore.RED}errors{Style.RESET_ALL}:')
			for i in range(len(errors)): print(f"{i+1} {errors[i]['title']}\n{errors[i]['url']}\n")

		return list(proceedings)

	
	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def accepted_papers(self):
		# TODO: Should check if the db previously loaded this conference. If so, then load from there and skip downloading
		# metadata again

		resp = urllib.request.urlopen(self.get_url(self.year))
		soup = BeautifulSoup(resp.read(), 'html.parser')
		tags = soup.find_all('li')
		
		papers = []

		for t in tags:
			atag = t.find('a')
			if atag['href'].startswith('/paper'):
				papers.append({'title': atag.text, 'href': ''.join([self.base, atag['href']]), 'authors': t.find('i').text})
		
		return self.get_metadata(papers)


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
			authors = [' '.join([a['given_name'], a['family_name']]) for a in p['authors']]
			affiliations = [a['institution'] for a in p['authors']]

			if (title_kw and has_title(title_kw, title)) or (author_kw and has_author(author_kw, authors)) or\
				(affiliation_kw and has_affiliation(affiliation_kw, affiliations)):
				extracted.append({'title': title, 'authors': authors, 'affiliations': affiliations, 'award': p['award'],
					'hash': p['hash'], 'url': p['url']})

		return extracted