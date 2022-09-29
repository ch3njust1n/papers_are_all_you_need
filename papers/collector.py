'''
'''

import os
import json
import logging
from re import S
import urllib.request
from pathlib import Path
from itertools import product
from threading import Thread
from urllib.error import URLError
from http.client import InvalidURL

import redis
from tqdm import tqdm
from colorama import Fore, Style

import papers.utils as utils


class Collector(object):
	'''
	inputs:
	logname  (str) Log name
	save_dir (str) Directory to save the collected results to
	'''
	def __init__(self, logname, save_dir, host='localhost', port=6379):
		self.host = host
		self.port = port
		self.cache = redis.Redis(host=host, port=port)
		self.logname = logname
		self.log = logging.getLogger(self.logname)
		self.save_dir = save_dir
		self.cache_dir = '.cache'
  
		if not os.path.exists(self.cache_dir):
			os.mkdir(self.cache_dir)
		
  
	'''
	inputs:
	cache (redis) Redis cache object
	'''
	def reload(self):
	 
		if len(os.listdir(self.save_dir)) == 0:
			self.cache.flushall()
			self.cache.flushdb()
	 
		try:
			most_recent = max([f for f in os.listdir(self.cache_dir) if f.endswith('.json')], key=os.path.getctime)
			
			if not most_recent:
				return
			
			with open(most_recent, 'r') as file:
				data = json.load(file)
				for key, value in data.items():
					self.cache.set(key, value)
	 
		except ValueError:
			return
		
	
	'''
	Download a paper.

	inputs:
	url      (str) Link to paper
	save_dir (str) Directory to save to
	filename (str) Name of file

	outputs:
	True if downloaded, else False
	'''
	def download(self, url, save_dir, filename):
		paper_urls = []
		if isinstance(url, str): paper_urls.append(url)
		if isinstance(url, list): paper_urls.extend(url)

		try:
			save_path = os.path.join(save_dir, filename)

			if not Path(save_path).is_file():
				files = []
				for i, link in enumerate(paper_urls):
					try:
						with urllib.request.urlopen(link) as resp, open(save_path, 'wb') as out:
							save_name = f'{save_path}_{i}.pdf' if i > 0 else f'{save_path}.pdf'
							file, headers = urllib.request.urlretrieve(link, save_name)
							if file: files.append(save_name)
					except InvalidURL as e:
						self.log.debug(f'{e} - {filename}')

				return all(os.path.exists(f) for f in files)
			else:
				return True
		except URLError as e:
			return False


	'''
	inputs:
	authors          (list)  		  List of strings of authors
	affiliations 	 (list) 		  List of author affiliations
	first_name       (bool, optional) Extract first name of first author only. Default: False.
	last_name        (bool, optional) Extract last name of first author only. Default: False.
	author_only 	 (bool, optional) Extract first author's name only. Default: True.
	affiliation_only (bool, optional) Extract first author's affiliation only. Default: False.

	outputs:
	name (str) First author
	aff  (str) First author's affiliation
	'''
	def get_first_author(self, authors, affiliations, last_name=False, first_name=False, author_only=True, affilition_only=False):

		name, aff = authors[0], affiliations[0]

		if first_name and author_only: return name.split(' ')[0], ''
		if last_name and author_only: return name.split(' ')[-1], ''
		if first_name and not author_only: return name.split(' ')[0], aff
		if last_name and not author_only: return name.split(' ')[-1], aff
		if author_only: return name, ''
		if affilition_only: return '', aff
		return name, aff


	'''
	Format filename

	inputs:
	filename 	(str) Format for filename. Any permutation of 'year-auth-title'. Does not
					  need to contain all three.
	year  	 	(str) Year of paper
	name  	 	(str) Author name
	affiliation (str) Affiliation
	title 	 	(str) Paper title

	outputs:
	filename (str) Formatted filename
	'''
	def format_filename(self, filename, year, auth, affiliation, title):

		title = title.lower().replace(':', '').replace('/', ' ')
		filename = filename.replace('author', auth.lower())
		filename = filename.replace('year', str(year))
		filename = filename.replace('affiliation', affiliation)

		return filename.replace('title', title)



	'''
	Format and download paper, and set cache checkpoint

	inputs:
	title        (str)  Paper title
	authors      (list) Authors
	affiliations (list) Author affiliations
	url          (str)  PDF url
	year         (str)  Publication year
	template     (str)  File name template
	save_dir     (str)  Save directory
	'''
	def save_paper(self, title, authors, affiliations, url, year, template, save_dir):
     
		try:
			auth, aff = self.get_first_author(authors, affiliations, last_name=True)
			filename = self.format_filename(template, year, auth, aff, title)
			ok = self.download(url, save_dir, filename)
			self.cache.set(title.lower(), int(ok))
			utils.delete_zerofiles(save_dir)
			
			if not ok:
				self.log.debug(f'{Fore.RED}err{Style.RESET_ALL}: {title}')
		except Exception as e:
			self.log.debug(f'{Fore.RED}err{Style.RESET_ALL}: {title}')

	
	'''
	Main execution loop for scraping and downloading papers.

	inputs:
	papers   (list) List of dicts of paper meta data
	save_dir (str)  Save directory
	'''
	def scrape(self, papers, year, template, save_dir):

		def batch(iterable, size=1):

			l = len(iterable)
			for i in range(0, l, size):
				yield iterable[i:min(i + size, l)]

		for block in batch(papers, 16):
			procs = []
			for paper in block:
				if self.cache.get(paper['title'].lower()): continue
				args = (paper['title'], paper['authors'], paper['affiliations'], paper['url'], year, template, save_dir,)
				procs.append(Thread(target=self.save_paper, args=args))
				
			for p in procs: p.start()
			for p in procs: p.join()

		_, _, files = next(os.walk(save_dir))
		successes = len([f for f in files if f.endswith('.pdf')])
		self.log.info(f'downloaded {successes} papers')
 


	'''
	inputs:
	conferences    (str)  			Conference name
	years 		   (str)  			Year of conference
	template 	   (str)  			String of file name template
	title_kw 	   (list) 			Title keywords
	author_kw 	   (list) 			Author names
	affiliation_kw (list) 			Afiliation/lab names
	mode           (str, optional)  If 'download', download papers.
									If 'search', search papers
									Default: 'download'
	checkpoint     (bool, optional) If True, resume downloading from checkpoint. Default: True
	logname        (str, optional)  Name of logfile. Default: 'default.log'
	'''
	def collect(self, conferences, years, template, title_kw, author_kw, affiliation_kw, mode='download', checkpoint=True, logname='default.log'):
	
		self.reload()
	
		conferences = utils.parse_conferences(conferences)
		years = utils.get_years(years)
		total = len(conferences) * len(years)
	
		conf_years = product(conferences, years)
	
		with tqdm(total=total) as pbar:
			for conf, yr in conf_years:
				cf = utils.get_conf(conf, yr)

				if not cf: return

				try:
					papers = cf.accepted_papers()
					total_accepted = len(papers)
			
					if total_accepted:
						papers = cf.query_papers(papers, title_kw=title_kw, author_kw=author_kw, affiliation_kw=affiliation_kw)
						self.log.info(f'{conf} {yr} - found {len(papers)} papers of {total_accepted} total accepted papers')
		
						if mode == 'download':
							self.scrape(papers, yr, template, self.save_dir)
						if mode == 'search':
							for p in papers:
								if p: self.log.info(p['title'])
				except Exception as e:
					self.log.debug(f'{Fore.RED}err{Style.RESET_ALL}: {e}')
				
				pbar.update(1)