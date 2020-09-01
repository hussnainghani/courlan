"""
Unit tests for the courlan package.
"""

## This file is available from https://github.com/adbar/courlan
## under GNU GPL v3 license

import os
import sys

from unittest.mock import patch

import pytest

from courlan.clean import clean_url, normalize_url
from courlan.cli import parse_args
from courlan.core import check_url, sample_urls, validate_url
from courlan.filters import extensionfilter, spamfilter, typefilter


def test_clean():
    assert clean_url('  https://www.dwds.de') == 'https://www.dwds.de'
    assert clean_url('HTTPS://WWW.DWDS.DE/') == 'https://www.dwds.de'
    assert clean_url('<![CDATA[https://www.dwds.de]]>') == 'https://www.dwds.de'
    assert clean_url('https://www.dwds.de/test?param=test&amp;other=test') == 'https://www.dwds.de/test?param=test&other=test'
    assert clean_url('https://www.dwds.de/garbledhttps://www.dwds.de/') == 'https://www.dwds.de'
    # exception for archive URLs
    assert clean_url('https://web.archive.org/web/20131021165347/https://www.imdb.com/') == 'https://web.archive.org/web/20131021165347/https://www.imdb.com'


def test_extensionfilter():
    assert extensionfilter('http://www.example.org/test.js') is False


def test_spamfilter():
    assert spamfilter('http://www.example.org/cams/test.html') is False
    assert spamfilter('http://www.example.org/test.html') is True


def test_typefilter():
    assert typefilter('http://www.example.org/feed') is False
    assert typefilter('http://www.example.org/category/123') is False
    assert typefilter('http://www.example.org/test.xml?param=test', strict=True) is False
    assert typefilter('http://www.example.org/test.asp') is True
    assert typefilter('http://ads.example.org/') is False
    assert typefilter('http://my-videos.com/') is False
    assert typefilter('http://www.example.org/index', strict=True) is False
    assert typefilter('http://www.example.org/index.html', strict=True) is False


def test_validate():
    assert validate_url('ntp://www.test.org/test')[0] is False
    assert validate_url('ftps://www.test.org/test')[0] is False
    assert validate_url('http://t.g/test')[0] is False
    assert validate_url('http://test.org/test')[0] is True


def test_defrag():
    assert normalize_url('http://test.net/foo.html#bar') == 'http://test.net/foo.html'
    assert normalize_url('http://test.net/foo.html#:~:text=night-,vision') == 'http://test.net/foo.html'


def test_qelems():
    assert normalize_url('http://test.net/foo.html?utm_source=twitter') == 'http://test.net/foo.html'
    assert normalize_url('http://test.net/foo.html?utm_source=twitter&page=2') == 'http://test.net/foo.html?page=2'
    assert normalize_url('http://test.net/foo.html?page=2&lang=en') == 'http://test.net/foo.html?page=2&lang=en'
    with pytest.raises(ValueError):
        assert normalize_url('http://test.net/foo.html?page=2&lang=en', with_language=True)


def test_urlcheck():
    assert check_url('AAA') is None
    assert check_url('http://ab') is None
    assert check_url('ftps://example.org/') is None
    assert check_url('http://t.g/test') is None
    assert check_url('https://www.dwds.de/test?param=test&amp;other=test') == ('https://www.dwds.de/test', 'dwds.de')
    assert check_url('http://example.com/index.html#term')[0] == 'http://example.com/index.html'
    assert check_url('http://example.com/test.js') is None
    assert check_url('http://example.com/test.html?lang=en', with_language=True) is None
    assert check_url('http://example.com/test.html?lang=en', with_language=False) is not None
    assert check_url('http://twitter.com/') is None
    # assert urlcheck('http://example.invalid/', False) is None
    assert check_url('https://www.httpbin.org/status/200', with_redirects=True) == ('https://www.httpbin.org/status/200', 'httpbin.org')
    assert check_url('https://www.httpbin.org/status/404', with_redirects=True) is None
    assert check_url('https://www.ht.or', with_redirects=True) is None
    assert check_url('http://www.example') is not None


def test_cli():
    '''test the command-line interface'''
    testargs = ['', '-i', 'input.txt', '--outputfile', 'output.txt', '-v']
    with patch.object(sys, 'argv', testargs):
        args = parse_args(testargs)
    assert args.inputfile == 'input.txt'
    assert args.outputfile == 'output.txt'
    assert args.verbose is True
    assert os.system('courlan --help') == 0  # exit status


def test_sample():
    assert len(sample_urls(['http://test.org/test1', 'http://test.org/test2'], 0)) == 0
    # assert len(sample_urls(['http://test.org/test1', 'http://test.org/test2'], 1)) == 1
    mylist = ['http://t.o/t1', 'http://test.org/test1', 'http://test.org/test2', 'http://test2.org/test2']
    assert len(sample_urls(mylist, 1, verbose=True)) == 1
    assert len(sample_urls(mylist, 1, exclude_min=10, verbose=True)) == 0
    assert len(sample_urls(mylist, 1, exclude_max=1, verbose=True)) == 0


def test_examples():
    '''Test README examples'''
    assert check_url('1234') is None
    assert clean_url('HTTPS://WWW.DWDS.DE/') == 'https://www.dwds.de'
    assert validate_url('1234')[0] is False
