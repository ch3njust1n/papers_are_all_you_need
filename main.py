'''
Script for downloading machine learning conference papers

Author: Justin Chen
Date: 11/5/2020
'''

import os
import shutil
import argparse
import unicodedata
import configparser
import urllib.request
from urllib.error import URLError, HTTPError
from multiprocessing import Process, cpu_count

from tqdm import tqdm
from bs4 import BeautifulSoup


'''
inputs:
authors          (list)  		  Single string of authors
last_name        (bool, optional) Extract last name of first author only. Default: False.
first_name       (bool, optional) Extract first name of first author only. Default: False.
affiliation      (bool, optional) Extract first author's affiliation. Default: False.
affiliation_only (bool, optional) Extract first author's affiliation only. Default: False.

outputs:
name (str) First author or affiliation
'''
def get_first_author(authors, last_name=False, first_name=False, affiliation=True, affilition_only=False):
	name, affiliation = authors[0]

	if not affiliation: return name
	if affilition_only: return affiliation
	if last_name: return name.split(' ')[-1]
	elif first_name: return name.split(' ')[0]
	return f'{name} {affiliation}'


'''
Combine the authors list from the conference with the authors list on Arxiv.
Some names on the conference website are not in English. Assuming that all the names on
Arxiv are in English, but Arxiv does not have the affiliation information.

Assuming NIPS for now. Will handle other conferences later.

inputs:
conf_authors  (str)  String of author names extracted from the conference website
arxiv_authors (list) List of author names extracted from Arxiv

output:
authors (list) List of authors names in English as keys and affiliation as values
'''
def format_authors(conf_authors, arxiv_authors):
	# NIPS author string format
	authors = []
	nips_authors = conf_authors.split(' · ')

	'''
	In some cases, authors lists may differ. Either author(s) are missing or there 
	are extra the order may also differ
	'''
	for nips, arxiv in zip(nips_authors, arxiv_authors):
		nips = nips.split('(')
		affiliation = ' '.join(nips[-1])[:-1]
		name = nips[0]
		authors.append((arxiv, affiliation))

	return authors


'''
Get all accepted papers from NIPS. In some cases, the name of the final submission is different
from the name of the paper on Arxiv. May need to use binary classifier for these cases.

inputs:
url            (str)  		    Link to accepted papers page
title_kw       (list, optional) Keywords to match in title
author_kw      (list, optional) Names to match in authors list
affiliation_kw (list, optional) Names to match in affiliation list

outputs:
papers (dict) Dictionary of accepted papers with keys as the paper title and value as the authors.
'''
def accepted_papers(url, title_kw=None, author_kw=None, affiliation_kw=None):
	if title_kw: title_kw = [w.lower() for w in title_kw if len(w) > 0]
	if author_kw: author_kw = [w.lower() for w in author_kw if len(w) > 0]
	if affiliation_kw: affiliation_kw = [w.lower() for w in affiliation_kw if len(w) > 0]

	resp = urllib.request.urlopen(url)
	soup = BeautifulSoup(resp.read(), 'html.parser')
	main = soup.find('main', {'id': 'main'})
	papers = main.find_all('div')[-1].find_all('p')

	extracted = {}
	has_title = lambda words, title: any(word in title.lower() for word in words)
	has_author = lambda names, authors: any(n in authors.lower() for n in names)
	has_affiliation = lambda aff, authors: any(a in authors.lower() for a in aff)

	for p in papers[2:]:
		title = p.find('b').text
		authors = p.find('i').text

		if (title_kw and has_title(title_kw, title)) or (author_kw and has_author(author_kw, authors)) or\
			(affiliation_kw and has_affiliation(affiliation_kw, authors)):
			extracted[title] = authors

	return extracted


'''
Assumes the same url format for machine learning conferences

inputs:
url (str) Conference accepted papers url

output:
year (str) Year of accepted papers
'''
def get_year(url):
	return url.split('/')[-2]


'''
Format filename

inputs:
filename (str) Format for filename. Any permutation of 'year-auth-title'. Does not
			   need to contain all three.
year  	 (str) Year of paper
name  	 (str) Author name
title 	 (str) Paper title

outputs:
filename (str) Formatted filename
'''
def format_filename(filename, year, auth, title):
	title = title.lower().replace(':', '')
	filename = filename.replace('author', auth.lower())
	filename = filename.replace('year', year)

	return filename.replace('title', title)+'.pdf'


'''
Get specific version of the pdf. If version cannot be found, the latest version is returned.

inputs:
pdf_ids (list) 			Collection of Arxiv PDF ids. List should contain same Arxiv ids.
version (int, optional) Version number starting at 1. -1 for the latest version. Default: -1.

outputs:
pdf_id (str) PDF id of version number
'''
def get_pdf_version(pdf_ids, version=-1):
	version_ids, v = [], 1

	for p in pdf_ids:
		i = p['href'].rfind('v')+1
		v = int(p['href'][i:])
		if v == version: return v
		version_ids.append(v)

	return max(version_ids)


'''
Check that the pdf id matches the title of the arxiv page
inputs:
pdf_id  (str)           Arxiv pdf id
title  	(str) 			Given title to search for
version (int, optional) PDF version

outputs:
match (bool) True if the id matches the given title
'''
def verify_pdf(pdf_id, title, version=''):
	url, resp = f'https://arxiv.org/abs/{pdf_id}', ''
	
	if len(version) > 0: url += f'v{version}'

	try:
		resp = urllib.request.urlopen(url)
		soup = BeautifulSoup(resp.read(), 'html.parser')
		page_title = soup.find('h1', {'class': 'title mathjax'}).find_all(text=True)
		return title.strip() in page_title
	except (HTTPError, URLError) as e:
		print(e)
		return False


'''
Remove control characters

inputs:
s (str) String with control characters

output:
s (str) Cleaned string
'''
def remove_ctrl_char(s):
	s = ''.join(c for c in s if unicodedata.category(c)[0]!='C')
	return ' '.join(s.split('\t'))


'''
Arxiv always displays the latest version of the paper. When the request is made, only the current
version of the paper will appear in the html.

inputs:
title   (str) 			 Title of paper
latest  (bool, optional) If True, get the latest version of the paper
version (int, optional)  PDF version

outputs:
href    (str) PDF URL
updated (str) Date of PDF
authors (list)
'''
def get_pdf_link(title, latest=True, version=''):
	title_query = remove_ctrl_char(title).replace(' ', '%20').replace(':', '')
	query = f'http://export.arxiv.org/api/query?search_query={title_query}'
	resp = urllib.request.urlopen(query)
	soup = BeautifulSoup(resp.read(), 'html.parser')
	entries = soup.find_all('entry')
	url, updated, authors = None, '', []

	# It's possible that the authors did not upload their paper to Arxiv.
	for e in entries:
		if e.find('title').text == title:
			url = e.find('link', {'title': 'pdf'})['href']
			url = url[:url.rfind('v')]+'.pdf'
			updated = e.find('updated').text.split('T')[0]
			authors = [a.find('name').text for a in e.find_all('author')]

	return url, updated, authors


'''
Download a paper.

inputs:
url      (str) Link to paper
save_dir (str) Directory to save to
filename (str) Name of file

outputs:
True if downloaded, else False
'''
def download(url, save_dir, filename):
	save_path = os.path.join(save_dir, filename)

	with urllib.request.urlopen(url) as resp, open(save_path, 'wb') as out:
		# shutil.copyfileobj(resp, out)
		file, headers = urllib.request.urlretrieve(url, save_path)

		return len(file) > 0


def helper(title, conf_authors, template, save_dir):
	url, year, arxiv_authors = get_pdf_link(title)
	authors = format_authors(conf_authors, arxiv_authors)

	if len(authors) > 0:
		auth = get_first_author(authors, last_name=True)

		if url:
			year = year.split('-')[0]
			filename = format_filename(template, year, auth, title)
			download(url, save_dir, filename)


'''
Main execution loop for scraping and downloading papers.

inputs:
papers   (dict) Collection of papers
save_dir (str)  Save directory
'''
def scrape(papers, template, save_dir):
	# successes = 0

	def batch(iterable, size=1):
		l = len(iterable)
		for i in range(0, l, size):
			yield iterable[i:min(i + size, l)]

	pbar = tqdm(total=len(papers))

	for block in batch(list(papers.items()), cpu_count()):
		procs = [Process(target=helper, args=(title, conf_authors, template, save_dir,)) for title, conf_authors in block]
			
		for p in procs: p.start()
		for p in procs: p.join()

		pbar.update(len(block))

	pbar.close()
	_, _, files = next(os.walk(save_dir))
	successes = len(files)
	print(f'downloaded {successes} papers')


def main():
	config = configparser.ConfigParser(allow_no_value=True)
	config.read('config.ini')
	cfg = config['DEFAULT']

	url = cfg['url']
	title_kw = cfg['title_kw'].split(',')
	author_kw = cfg['author_kw'].split(',')
	affiliation_kw = cfg['affiliation_kw'].split(',')

	papers = accepted_papers(url, title_kw=title_kw, author_kw=author_kw, affiliation_kw=affiliation_kw)

	print(f'found: {len(papers)} papers')

	template = cfg['template']
	save_dir = cfg['save_dir']

	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 

	scrape(papers, template, save_dir)


if __name__ == '__main__':
	main()