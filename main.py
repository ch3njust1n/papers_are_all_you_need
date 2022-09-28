'''
Script for downloading machine learning conference papers

Author: Justin Chen
Date: 11/5/2020
'''
import os
import time
import configparser
from itertools import product
from multiprocessing import Process, Manager, cpu_count

from tqdm import tqdm

import papers.utils as utils


'''
inputs:
conferences    (str)  Conference name
years 		   (str)  Year of conference
save_dir 	   (str)  Directory to save papers to
template 	   (str)  String of file name template
title_kw 	   (list) Title keywords
author_kw 	   (list) Author names
affiliation_kw (list) Afiliation/lab names
'''
def collect(conferences, years, save_dir, template, title_kw, author_kw, affiliation_kw, mode='download'):
	conferences = utils.parse_conferences(conferences)
	years = utils.get_years(years)
	total = len(conferences) * len(years)
 
	conf_years = product(conferences, years)
 
	with tqdm(total=total) as pbar:
		for conf, yr in conf_years:
			cf = utils.get_conf(conf, yr)

			if not cf: return

			papers = cf.accepted_papers()
			total_accepted = len(papers)
	
			if total_accepted:
				papers = cf.query_papers(papers, title_kw=title_kw, author_kw=author_kw, affiliation_kw=affiliation_kw)
				print(f'{conf} {yr} - found {len(papers)} papers of {total_accepted} total accepted papers')

				if mode == 'download':
					utils.scrape(papers, yr, template, save_dir)
			
			pbar.update(1)


def main():

	config = configparser.ConfigParser(allow_no_value=True)
	config.read('config.ini')
	cfg = config['DEFAULT']

	conferences = cfg['conference']
	years = cfg['year']
	title_kw = cfg['title_kw'].split(',')
	author_kw = cfg['author_kw'].split(',')
	affiliation_kw = cfg['affiliation_kw'].split(',')
	template = cfg['template']
	save_dir = cfg['save_dir']
	mode = cfg['mode']

	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 
  
	if not mode.lower().strip() in {'search', 'download'}:
		raise ValueError(f'Invalid mode: {mode}')

	start_time = time.perf_counter()
	collect(conferences, years, save_dir, template, title_kw, author_kw, affiliation_kw, mode=mode)
	end_time = time.perf_counter()

	print(f'runtime: {end_time - start_time} (sec)')


if __name__ == '__main__':
	main()