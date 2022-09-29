'''
Script for downloading machine learning conference papers

Author: Justin Chen
Date: 11/5/2020
'''
import os
import time
import logging
import configparser

from papers.collector import Collector

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
	
	logname = save_dir.split('/')[-1]+'.log'
	logging.basicConfig(
     	level=logging.INFO, 
    	filename=logname,
     	filemode='w', 
      	format='%(name)s - %(levelname)s - %(message)s'
    )

	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 
  
	if not mode.lower().strip() in {'search', 'searches', 'download', 'downloads', 'stats', 'statistics', 'stat'}:
		raise ValueError(f'Invalid mode: {mode}')

	start_time = time.perf_counter()
	clt = Collector(logname, save_dir)
	clt.collect(conferences, years, template, title_kw, author_kw, affiliation_kw, mode=mode, logname=logname)
	end_time = time.perf_counter()

	print(f'runtime: {end_time - start_time} (sec)')


if __name__ == '__main__':
	main()