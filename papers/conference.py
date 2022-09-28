'''
'''
import sys
import json
import urllib.request

from colorama import Fore, Style


class Conference(object):
	def __init__(self, name, year):
		
		self.name = name
		self.year = str(year)
		self.conf = {
			frozenset({'nips', 'neurips'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/neurips',
			frozenset({'icml'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/icml',
			frozenset({'aistats'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/aistats',
			frozenset({'acml'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/acml',
			frozenset({'corl'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/corl',
			frozenset({'uai'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/uai',
			frozenset({'cvpr'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/cvpr',
			frozenset({'iccv'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/iccv',
			frozenset({'wacv'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/wacv',
			frozenset({'iclr'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/iclr',
			# 'emnlp': '',
			# 'aaai': '',
			# 'sysml': '',
			# 'naacl': '',
			# 'icme': '',
			# 'chil': '',
			# 'icip': '',
			# 'ijcai': '',
			# 'acl': '',
			# 'sigir': '',
			# 'iccv': '',
			# 'eccv': ''
		}
  
		for c in self.conf.keys():
			if name in c:
				self.repo = self.conf[c]
				break

		if not self.repo:
			raise ValueError(f'Conference {name} not supported.')


	'''
	Get meta data of accepted papers from pseudo-api

	outputs:
	data (list) List of dicts of paper meta data
	'''
	def accepted_papers(self):

		url = '/'.join([self.repo, f'{self.name}_{self.year}.json'])
  
		try:
			with urllib.request.urlopen(url) as file:
				return json.loads(file.read().decode())
		except urllib.error.HTTPError:
			return []


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
			if not p: continue
   
			title = p['title']
			
			try:
				authors = [' '.join([' '.join(a['given_name']), a['family_name']]) for a in p['authors']]
				affiliations = [a['institution'] for a in p['authors']]
			except:
				print(p)
				sys.exit()


			if (title_kw and has_title(title_kw, title)) or '*' in title_kw or\
			   (author_kw and has_author(author_kw, authors)) or\
			   (affiliation_kw and has_affiliation(affiliation_kw, affiliations)):

				extracted.append({
					'title': title, 
					'authors': authors, 
					'affiliations': affiliations, 
					'award': p.get('award', None),
					'hash': p.get('hash', None), 
					'url': p.get('url', None)
				})

		return extracted