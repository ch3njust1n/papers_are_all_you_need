"""
Author: Justin Chen
Date: 11/8/2020
"""
import os
import re
import json
import unicodedata
import urllib.request
from datetime import date
from urllib.error import URLError, HTTPError

from bs4 import BeautifulSoup

from papers.conference import Conference

CONFERENCES = {
    "aistats",
    "acml",
    "corl",
    "cvpr",
    "iccv",
    "iclr",
    "icml",
    "ijcai",
    "mlsys",
    "neurips",
    "nips",
    "uai",
    "wacv",
}

MIN_YEAR = 1969
MAX_YEAR = date.today().year


"""
Save json data

inputs:
filename (str)  Name of output file
data     (list) JSON object
"""


def save_json(save_dir, filename, data):

    with open(
        os.path.join(save_dir, filename + ".json"), "w", encoding="utf-8"
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


"""
Get the year generator
: For range of years e.g. 2010:2020
, List of years, not necessarily consecutive list e.g. 1987, 2018, 2020
# Single numbers for just that one year e.g. 2020
* All years from MIN_YEAR to MAX_YEAR inclusive

inputs:
year (str) Year designation

outputs:
years (list) List of years
"""


def get_years(year):

    if not year:
        raise ValueError("Invalid years specified")

    if year == "*":
        return range(MIN_YEAR, MAX_YEAR + 1)

    if re.match("\d+:\d+", year):
        year = year.split(":")
        return range(int(year[0]), int(year[1]) + 1)

    return [y for y in year.split(",") if len(y) > 0]


"""
Get specific version of the pdf. If version cannot be found, the latest version is returned.

inputs:
pdf_ids (list) 			Collection of Arxiv PDF ids. List should contain same Arxiv ids.
version (int, optional) Version number starting at 1. -1 for the latest version. Default: -1.

outputs:
pdf_id (str) PDF id of version number
"""


def get_pdf_version(pdf_ids, version=-1):

    version_ids, v = [], 1

    for p in pdf_ids:
        i = p["href"].rfind("v") + 1
        v = int(p["href"][i:])
        if v == version:
            return v
        version_ids.append(v)

    return max(version_ids)


"""
Check that the pdf id matches the title of the arxiv page
inputs:
pdf_id  (str)           Arxiv pdf id
title  	(str) 			Given title to search for
version (int, optional) PDF version

outputs:
match (bool) True if the id matches the given title
"""


def verify_pdf(pdf_id, title, version=""):

    url, resp = f"https://arxiv.org/abs/{pdf_id}", ""

    if len(version) > 0:
        url += f"v{version}"

    try:
        resp = urllib.request.urlopen(url)
        soup = BeautifulSoup(resp.read(), "html.parser")
        page_title = soup.find("h1", {"class": "title mathjax"}).find_all(text=True)
        return title.strip() in page_title
    except (HTTPError, URLError) as e:
        print(e)
        return False


"""
Remove control characters

inputs:
s (str) String with control characters

output:
s (str) Cleaned string
"""


def remove_ctrl_char(s):

    s = "".join(c for c in s if unicodedata.category(c)[0] != "C")
    return " ".join(s.split("\t"))


"""
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
"""


def get_arxiv_link(title, latest=True, version=""):

    title_query = remove_ctrl_char(title).replace(" ", "%20").replace(":", "")
    query = f"http://export.arxiv.org/api/query?search_query={title_query}"
    resp = urllib.request.urlopen(query)
    soup = BeautifulSoup(resp.read(), "html.parser")
    entries = soup.find_all("entry")
    url, updated, authors = None, "", []

    # It's possible that the authors did not upload their paper to Arxiv.
    for e in entries:
        if e.find("title").text == title:
            url = e.find("link", {"title": "pdf"})["href"]
            url = url[: url.rfind("v")] + ".pdf"
            updated = e.find("updated").text.split("T")[0]
            authors = [a.find("name").text for a in e.find_all("author")]

    return url, updated, authors


"""
inputs:
name (str) Name of conference
year (str) Year of conference

outputs:
conference (conference)
"""


def get_conf(name, year):

    name = name.lower().strip()

    if name in CONFERENCES:
        return Conference(name, year)

    print(f"{name} does not exist")
    return None


"""
inputs:
conferences (str) String list of conferences or special characters

outputs:
conferences (list) List of conference names
"""


def parse_conferences(conferences):
    if conferences == "*":
        return list(CONFERENCES)

    confs = [c.lower().strip() for c in conferences.split(",")]

    if not confs or not set(confs).issubset(CONFERENCES):
        raise ValueError(
            "One or more of the conference names are invalid or not supported."
        )

    return confs


"""
inputs:
dirname (string) Directory containing files to delete
"""


def delete_zerofiles(dirname):
    for filename in os.listdir(dirname):
        filepath = os.path.join(dirname, filename)
        try:
            if os.path.isfile(filepath) and os.stat(filepath).st_size == 0:
                os.remove(filepath)
        except FileNotFoundError:
            pass
