'''
Author: Justin Chen
Date: 11/8/2020
'''
import os
import re
import json
import platform
import unicodedata
import urllib.request
from urllib.error import URLError, HTTPError
from threading import Thread
from multiprocessing import Process, cpu_count

from tqdm import tqdm
from bs4 import BeautifulSoup
from colorama import Fore, Style


'''
Save json data

inputs:
filename (str)  Name of output file
data     (list) JSON object
'''
def save_json(save_dir, filename, data):
	with open(os.path.join(save_dir, filename+'.json'), 'w', encoding='utf-8') as file:
		json.dump(data, file, ensure_ascii=False, indent=4)


'''
Get the year generator
: For range of years e.g. 2010:2020
, List of years, not necessarily consecutive list e.g. 1987, 2018, 2020
# Single numbers for just that one year e.g. 2020

inputs:
year (str) Year designation

outputs:
years (list) List of years
'''
def get_years(year):
	if len(year) == 0: []

	if re.match('\d+:\d+', year):
		year = year.split(':') 
		return range(int(year[0]), int(year[1])+1)

	return [y for y in year.split(',') if len(y) > 0]


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
def format_filename(filename, year, auth, affiliation, title):
	title = title.lower().replace(':', '')
	filename = filename.replace('author', auth.lower())
	filename = filename.replace('year', year)
	filename = filename.replace('affiliation', affiliation)

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
def get_first_author(authors, affiliations, last_name=False, first_name=False, author_only=True, affilition_only=False):
	name, aff = authors[0], affiliations[0]

	if first_name and author_only: return name.split(' ')[0], ''
	if last_name and author_only: return name.split(' ')[-1], ''
	if first_name and not author_only: return name.split(' ')[0], aff
	if last_name and not author_only: return name.split(' ')[-1], aff
	if author_only: return name, ''
	if affilition_only: return '', aff
	return name, aff


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
def get_arxiv_link(title, latest=True, version=''):
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
	try:
		save_path = os.path.join(save_dir, filename)
		with urllib.request.urlopen(url) as resp, open(save_path, 'wb') as out:
			file, headers = urllib.request.urlretrieve(url, save_path)

			return len(file) > 0
	except URLError as e:
		return False


'''
Format and download paper

inputs:
title        (str)  Paper title
authors      (list) Authors
affiliations (list) Author affiliations
url          (str)  PDF url
year         (str)  Publication year
template     (str)  File name template
save_dir     (str)  Save directory
'''
def save_paper(title, authors, affiliations, url, year, template, save_dir):
	auth, aff = get_first_author(authors, affiliations, last_name=True)
	filename = format_filename(template, year, auth, aff, title)
	status = download(url, save_dir, filename)
	
	if not status: print(f'{Fore.RED}err{Style.RESET_ALL}: {title}')


'''
Main execution loop for scraping and downloading papers.

inputs:
papers   (list) List of dicts of paper meta data
save_dir (str)  Save directory
'''
def scrape(papers, year, template, save_dir):

	def batch(iterable, size=1):
		l = len(iterable)
		for i in range(0, l, size):
			yield iterable[i:min(i + size, l)]

	pbar = tqdm(total=len(papers))

	# for block in batch(papers, cpu_count()):
	for block in batch(papers, 16):
		procs = []
		for paper in block:
			args = (paper['title'], paper['authors'], paper['affiliations'], paper['url'], year, template, save_dir,)
			# procs.append(Process(target=save_paper, args=args))
			procs.append(Thread(target=save_paper, args=args))
			
		for p in procs: p.start()
		for p in procs: p.join()

		pbar.update(len(block))

	pbar.close()
	_, _, files = next(os.walk(save_dir))
	successes = len([f for f in files if f.endswith('.pdf')])
	print(f'downloaded {successes} papers')