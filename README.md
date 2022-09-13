# Papers Are All You Need

## Supported Conferences:

**NeurIPS**: 1987-2021

**ICML**: 2013-2022

**AISTATS**: 2007, 2009-2022

**CoRL**: 2017-2021

**ACML**: 2010-2021

**UAI** 2019-2022

**CVPR** 2013-2022

Download research papers:
1. Containing keywords in the title
2. By your favorite authors
3. By your favorite affiliations/ labs

Currently only supports NeurIPS. Looking for contributors to expand this to other conferences and expand the feature set!

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