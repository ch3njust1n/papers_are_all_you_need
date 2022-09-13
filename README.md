# Papers Are All You Need


**Metadata coverage**
|  Conference 	                               |  Years 	                  | Proceedings  | Links         | Authors       | Institutions  |
|----------------------------------------------|------------------------------|--------------|---------------|---------------|---------------|
|   [ACML](https://www.acml-conf.org/)         | 2010-2021                    | 12/13 (92%)  | 100%          | 100%          | 0%            |
|   [AISTATS](https://aistats.org/)            | 2007, 2009-2022              | 15/26 (58%)  | 100%          | 100%          | 0%            |
|   [CoRL](https://corl2022.org/)              | 2017-2021                    | 5/5   (100%) | 100%          | 100%          | 0%            |
|   [CVPR](https://www.thecvf.com/)            | 2013-2022                    | 10/35 (29%)  | 100%          | 100%          | 0%            |
|   [ICCV](https://www.thecvf.com/)            | 2013, 2015, 2017, 2019, 2021 | 5/18  (28%)  | 100%          | 100%          | 0%            |
|   [ICML](https://icml.cc/)                   | 2013-2022	                  | 10/21 (48%)  | 100%          | 100%          | 0%            |
|   [NeurIPS](https://nips.cc/)	               | 1987-2021                    | 35/35 (100%) | 100%          | 100%          | 0%            |
|   [UAI](https://www.auai.org/)               | 2019-2022                    | 4/37  (11%)  | 100%          | 100%          | 0%            |
|   [WACV](https://www.thecvf.com/)            | 2020-2022                    | 3/22  (14%)  | 100%          | 100%          | 0%            | 


Download research papers:
1. Containing keywords in the title
2. By your favorite authors


## Usage

Edit `config.ini` with your parameters. It's ok to leave `title_kw`, `author_kw`, or `affiliation_kw` blank.


### Confirguation options

```
conference     Name of conference
year           Year(s) of conference
title_kw       Keywords to search for in title of papers
author_kw      Names of authors to search for
affiliation_kw Names of affiliations/labs to search for
template       File name format for saving pdfs e.g. `year-author-title` will save papers 
               as the year the paper was last published, followed by the first author's name, 
               followed by the title, all in lower case. You can rearrange these three pieces.
save_dir       Directory to save pdfs to
```

```
[DEFAULT]
conference = neurips
year = 2020
title_kw = graph, message-passing, node
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/neurips
```
and then run

`python main.py`

### Search year range
```
[DEFAULT]
conference = neurips
year = 1987:2019
title_kw = graph, message-passing, node
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/neurips
```

### Search specific years
```
[DEFAULT]
conference = neurips
year = 1999, 2012, 2018
title_kw = graph, message-passing, node
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/neurips
```