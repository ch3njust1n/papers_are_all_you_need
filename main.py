'''
Script for downloading machine learning conference papers

Author: Justin Chen
Date: 11/5/2020
'''
import os
import time
import configparser
from multiprocessing import Process, Manager, cpu_count

from papers.conference import Conference
import papers.utils as utils


'''
inputs:
name (str) Name of conference
year (str) Year of conference

outputs:
conference (conference)
'''
def get_conf(name, year):

	name = name.lower()

	if name in ['nips', 'neurips']:
		return Conference(name, year)

	print(f'{name} does not exist')
	return None


'''
inputs:
name 		   (str)  Conference name
year 		   (str)  Year of conference
save_dir 	   (str)  Directory to save papers to
template 	   (str)  String of file name template
title_kw 	   (list) Title keywords
author_kw 	   (list) Author names
affiliation_kw (list) Afiliation/lab names
'''
def collect(name, year, save_dir, template, title_kw, author_kw, affiliation_kw):

	for yr in utils.get_years(year):
		cf = get_conf(name, yr)

		if not cf: return

		papers = cf.accepted_papers()
		total_accepted = len(papers)
		papers = cf.query_papers(papers, title_kw=title_kw, author_kw=author_kw, affiliation_kw=affiliation_kw)

		print(f'{name} {yr} - found {len(papers)} papers')

		utils.scrape(papers, yr, template, save_dir)


def main():

	config = configparser.ConfigParser(allow_no_value=True)
	config.read('config.ini')
	cfg = config['DEFAULT']

	name = cfg['conference']
	year = cfg['year']
	title_kw = cfg['title_kw'].split(',')
	author_kw = cfg['author_kw'].split(',')
	affiliation_kw = cfg['affiliation_kw'].split(',')
	template = cfg['template']
	save_dir = cfg['save_dir']

	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 

	start_time = time.time()
	collect(name, year, save_dir, template, title_kw, author_kw, affiliation_kw)
	end_time = time.time()

	print(f'runtime: {end_time - start_time} (sec)')


if __name__ == '__main__':
	main()