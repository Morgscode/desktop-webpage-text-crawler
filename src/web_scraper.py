# packages = { BeautifulSoup: html-parsing }
# This script will index all of the text content on webapges found within the NAV element of a website
# pass the website you want to index in the target_url variable on line 15

import sys

from urllib.request import urlopen, URLError
from urllib.error import HTTPError
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def get_webpage_html(url: str):
    try:
        # lets request the webpage html content
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        # if it fails, let's encode our error as a string and write it to the logs
        error = "Web-scraper error at line 52... error code is: {errcode}; error reason is: {errreason}\n".format(
            errcode=e.code, errreason=e.reason)
        error_file = open("./web-scraper-logs/error.txt", "a+")
        error_file.write(error)
        error_file.close()
        return false
    else:
        return html


def convert_html_to_soup_obj(html):
    # lets store the html as a utf-8 encoded string
    html_string = html.read().decode('utf-8')

    # let's parse the html into an object with BeautifulSoup
    html_soup = BeautifulSoup(html_string, 'html.parser')

    return html_soup


def get_webpage_links_in_nav(html: BeautifulSoup):
    links = []

    for link in html.nav.find_all('a'):
        page_link = link.get('href')

        if page_link != "#":
            links.append(page_link)

    return links


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content
