# packages = { BeautifulSoup: html-parsing }
# This script will index all of the text content on webapges found within the NAV element of a website
# pass the website you want to index in the target_url variable on line 15

import sys

from urllib.request import urlopen
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
        error = "Web-scraper error in get_webpage_page_html fn... error code is: {errcode}; error reason is: {errreason}\n".format(
            errcode=e.code, errreason=e.reason)

        with open("./web-scraper-logs/error.txt", "a+") as error_file:

            error_file.write(error)

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

    # we need to asses if the page has a nav before we can look for links
    nav = html.find('nav')

    if nav:
        # let's get the href of every link
        for link in html.nav.find_all('a'):
            page_link = link.get('href')
            # let's only push urls
            if page_link != "#":
                links.append(page_link)
    # we'll return either an empty, or filled list
    return links


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content
