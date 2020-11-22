import sys
import re

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
from http.client import HTTPResponse
from bs4 import BeautifulSoup


def get_webpage_html(url: str):
    if url != "/":
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


def convert_html_to_soup_obj(html: HTTPResponse):

    if not html is None:
        # lets store the html as a utf-8 encoded string
        html_string = html.read().decode('utf-8')

        # let's parse the html into an object with BeautifulSoup
        html_soup = BeautifulSoup(html_string, 'html.parser')

        return html_soup
    else:
        return False

def get_webpage_links_in_navs(html: BeautifulSoup):
    links = []
    # we need to asses if the page has a nav before we can look for links
    navs = html.find_all('nav')
    if navs:
        for nav in navs:
            # let's get the href of every link
            for link in nav.find_all('a'):
                page_link = link.get('href')

                if page_link not in links:
                    print(page_link)
                    # let's only push urls that are valid, and havn't been indexed in this fn
                    # this regexp will pick up 'tel:, mailto: and #' hrefs
                    page_link_regexp = re.compile(
                        r'((mailto:|tel:)([A-z]+|[0-9])+|#|)')
                    mo = page_link_regexp.search(page_link)
                    if mo is None:
                        links.append(page_link)
    # we'll return either an empty, or filled list
    print(links)
    return links


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content
