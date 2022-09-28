# Papers Are All You Need


**[Metadata](https://github.com/ch3njust1n/conference_metadata) coverage**
|  Conference 	                               |  Years 	                  | Proceedings  | Links         | Authors       | Institutions  |
|----------------------------------------------|------------------------------|--------------|---------------|---------------|---------------|
|   [ACML](https://www.acml-conf.org/)         | 2010-2021                    | 12/13 (92%)  | 100%          | 100%          | 0%            |
|   [AISTATS](https://aistats.org/)            | 2007, 2009-2022              | 15/26 (58%)  | 100%          | 100%          | 0%            |
|   [CoRL](https://corl2022.org/)              | 2017-2021                    | 5/5   (100%) | 100%          | 100%          | 0%            |
|   [CVPR](https://www.thecvf.com/)            | 2013-2022                    | 10/35 (29%)  | 100%          | 100%          | 0%            |
|   [ICCV](https://www.thecvf.com/)            | 2013, 2015, 2017, 2019, 2021 | 5/18  (28%)  | 100%          | 100%          | 0%            |
|   [ICLR](https://iclr.cc/)                   | 2013-2022   	              | 10/10 (100%) | 100%          | 100%          | 0%            |
|   [ICML](https://icml.cc/)                   | 2013-2022	                  | 10/21 (48%)  | 100%          | 100%          | 0%            |
|   [NeurIPS](https://nips.cc/)	               | 1987-2021                    | 35/35 (100%) | 100%          | 100%          | 0%            |
|   [UAI](https://www.auai.org/)               | 2019-2022                    | 4/37  (11%)  | 100%          | 100%          | 0%            |
|   [WACV](https://www.thecvf.com/)            | 2020-2022                    | 3/22  (14%)  | 100%          | 100%          | 0%            | 


## Setup

1. `chmod +x setup.sh`
2. `./setup.sh`


## Usage

Edit `config.ini` with your parameters. It's ok to leave `title_kw`, `author_kw`, or `affiliation_kw` blank.


### Confirguation options

```
conference     Name of conferences
year           Year(s) of conference(s)
title_kw       Keywords to search for in title of papers
author_kw      Names of authors to search for
affiliation_kw Names of affiliations/labs to search for
template       File name format for saving pdfs e.g. `year-author-title` will save papers 
               as the year the paper was last published, followed by the first author's name, 
               followed by the title, all in lower case. You can rearrange these three pieces.
save_dir       Directory to save pdfs to
mode           Default mode "download" is to download all papers. If set to "search", it will 
               just find available papers, but will not download them.
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
mode = download
```
and then run

`python main.py`

### Search all conferences
```
[DEFAULT]
conference = *
year = 2021, 2022
title_kw = graph, message-passing, node
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/all_confs_2021_2022
mode = search
```

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
mode = search
```

### Search every proceeding across all conferences
```
[DEFAULT]
conference = *
year = *
title_kw = graph, message-passing, node
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/grid_search
mode = search
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
mode = download
```

### Download all titles
```
[DEFAULT]
conference = neurips
year = 1999, 2012, 2018
title_kw = *
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Downloads/neurips
mode = download
```