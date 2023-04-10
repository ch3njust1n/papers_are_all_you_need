import os
import tempfile
from unittest import mock

import pytest
import redis

from papers.collector import Collector


@pytest.fixture
def mock_collector():
    logname = "test.log"
    save_dir = tempfile.mkdtemp()
    host = "localhost"
    port = 6379
    clear_cache = False

    collector = Collector(logname, save_dir, host, port, clear_cache)
    return collector


@pytest.fixture
def mock_redis():
    return mock.MagicMock(spec=redis.Redis)


@pytest.fixture
def mock_paper():
    return {
        "title": "Sample Title",
        "authors": ["John Doe"],
        "affiliations": ["University of Nowhere"],
        "url": "https://example.com/sample.pdf",
        "year": "2022",
    }


def test_redis_status(mock_collector):
    with mock.patch("papers.collector.redis.Redis.ping", return_value=True):
        assert mock_collector.redis_status() is True


def test_redis_status_failure(mock_collector):
    with mock.patch(
        "papers.collector.redis.Redis.ping",
        side_effect=redis.exceptions.ConnectionError(),
    ):
        with pytest.raises(SystemExit):
            mock_collector.redis_status()


def test_download(mock_collector, mock_paper):
    with tempfile.TemporaryDirectory() as tmp_dir:
        save_dir = tmp_dir
        url = mock_paper["url"]
        filename = "sample_title.pdf"

        with mock.patch("papers.collector.urllib.request.urlopen") as mock_urlopen:
            with mock.patch(
                "papers.collector.urllib.request.urlretrieve"
            ) as mock_urlretrieve:
                mock_urlretrieve.return_value = (os.path.join(save_dir, filename), None)
                result = mock_collector.download(url, save_dir, filename)

        expected_filepath = os.path.join(save_dir, filename)
        assert not result
        assert os.path.exists(expected_filepath)


def test_get_first_author(mock_collector, mock_paper):
    authors = mock_paper["authors"]
    affiliations = mock_paper["affiliations"]

    first_author, first_affiliation = mock_collector.get_first_author(
        authors, affiliations, author_only=False
    )

    assert first_author == "John Doe"
    assert first_affiliation == "University of Nowhere"


def test_format_filename(mock_collector, mock_paper):
    filename = "year-author-title"
    year = mock_paper["year"]
    auth = mock_paper["authors"][0].lower()
    affiliation = mock_paper["affiliations"][0]
    title = mock_paper["title"].lower().replace(":", "").replace("/", " ")

    formatted_filename = mock_collector.format_filename(
        filename, year, auth, affiliation, title
    )
    expected_filename = f"{year}-{auth}-{title}"
    assert formatted_filename == expected_filename


def test_save_paper(mock_collector, mock_paper):
    with tempfile.TemporaryDirectory() as tmp_dir:
        title = mock_paper["title"]
        authors = mock_paper["authors"]
        affiliations = mock_paper["affiliations"]
        url = mock_paper["url"]
        year = mock_paper["year"]
        template = "year-author-title"
        save_dir = tmp_dir

        with mock.patch("papers.collector.Collector.download", return_value=True):
            mock_collector.save_paper(
                title, authors, affiliations, url, year, template, save_dir
            )

        assert mock_collector.cache.get
