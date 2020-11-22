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

    # we need to asses if the page has any nav[s] before we can look for links
    navs = html.find_all('nav')

    if navs:

        for nav in navs:
            # this will allow us to assess ALL children of the nav
            for child in nav.children:
                # this will come to us as a NavigableString
                # let's cast it back to a string
                child_html = str(child)
                # and parse it into a soup object
                child_html_soup = BeautifulSoup(child_html, 'html.parser')
                # extract all the link tags
                page_link_tags = child_html_soup.find_all('a')

                if page_link_tags:

                    for page_link in page_link_tags:
                        # let's get the href of every link
                        location = page_link.get('href')

                        if location not in links:
                            # let's only continue with urls that are valid, and havn't been indexed in this fn
                            # this regexp will pick up 'tel:, mailto: and #' hrefs
                            page_link_regexp = re.compile(
                                r'((mailto:|tel:)([A-z]+|[0-9])+|#|)')
                            page_link_regexp_mo = page_link_regexp.search(
                                str(location))

                            if not page_link_regexp_mo.group():
                                # we need to add some logic to check for a domain
                                # if not, let's retieve and parse the target url
                                # and append the scheme and netloc to the location
                                links.append(location)

    # we'll return either an empty, or filled list
    return links


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content
