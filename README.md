# Papers Are All You Need

Download research papers:
1. Containing keywords in the title
2. By your favorite authors
3. By your favorite affiliations/ labs

Currently only supports NeurIPS. Looking for contributors to expand this to other conferences and expand the feature set!

## Usage

Edit `config.ini` with your parameters. It's ok to leave `title_kw`, `author_kw`, or `affiliation_kw` blank.

`template` is how your research paper file names will be formatted e.g. `year-author-title` will save papers as the year the paper was last updated on Arxiv, followed by the first author's last name, followed by the title, all in lower case. You can rearrange these three pieces.

```
[DEFAULT]
url = https://nips.cc/Conferences/2020/AcceptedPapersInitial
title_kw = graph
author_kw = 
affiliation_kw = 
template = year-author-title
save_dir = /Users/justin/Downloads/nips2020
```
and then run

`python main.py`