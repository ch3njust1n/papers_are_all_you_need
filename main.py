'''
Script for downloading machine learning conference papers

Author: Justin Chen
Date: 11/5/2020
'''
import os
import argparse
import configparser

from conference import conference as conf
from conference import utils


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

	cf = None
	if name.lower() in ['nips', 'neurips']:
		cf = conf.NeurIPS(year)

	papers = cf.accepted_papers()
	utils.save_json(save_dir, f'neurips_{year}', papers)
	papers = cf.query_papers(papers, title_kw=title_kw, author_kw=author_kw, affiliation_kw=affiliation_kw)

	print(f'found: {len(papers)} papers')

	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 

	# utils.scrape(papers, year, template, save_dir)


if __name__ == '__main__':
	main()