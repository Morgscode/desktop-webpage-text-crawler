import sys
import re

from urllib.parse import urlparse
from bs4 import BeautifulSoup

import requests


def get_webpage_html(url: str):

    # lets request the webpage html content
    html = requests.get(url)

    try:
        if html.status_code != 200:
            raise Exception("Web-scraper error in get_webpage_page_html fn... error code is: {errcode}; error reason is: {errreason} at url: {url}\n".format(
                errcode=html.status_code, errreason=html.reason, url=url))

        # regardsless of result, we return the http response
        return html
    except Exception as e:

        with open("./web-scraper-logs/error.txt", "a+") as error_file:
            error_file.write(str(e))

        # regardsless of result, we return the http response
        return html


def convert_html_to_soup_obj(html: requests.Response):
    # lets store the html as a utf-8 encoded string
    html_string = html.text

    # let's parse the html into an object with BeautifulSoup
    html_soup = BeautifulSoup(html_string, 'html.parser')

    return html_soup


def get_valid_webpage_link_hrefs_in_navs(html: BeautifulSoup):
    link_hrefs = []
    # we need to asses if the page has a nav before we can look for _hrefs
    navs = html.find_all('nav')

    if navs:

        for nav in navs:

            # let's get the href of every link
            for link in nav.find_all('a'):
                page_link = link.get('href')

                if page_link and page_link not in link_hrefs:

                    # let's only push urls that are valid, are not pdf files
                    # and havn't been indexed in this fn

                    # this regexp will pick up
                    # hrefs that start with 'tel:, mailto:
                    # and hrefs that end with .pdf
                    page_link_regexp = re.compile(
                        r'^(mailto:[A-z]+|tel:\+?[0-9]+|#)|.pdf$')

                    mo = page_link_regexp.search(page_link)

                    # if regexp does not match, we can add it as
                    # a valid href
                    if mo is None:
                        link_hrefs.append(page_link)

    # we'll return either an empty, or filled list
    return link_hrefs


def get_internal_links_from_webpage(html: BeautifulSoup, target_url: str):
    valid_internal_links = []

    links = html.find_all("a")

    if links:

        for link in links:

            # lets extract all the hrefs
            link_href = link.get('href')

            # lets only work with hrefs we haven't indexed yet
            if link_href and link_href not in valid_internal_links:

                # lets extract te target domain to format
                # hrefs which aren't valid urls
                parsed_target_url = urlparse(target_url)
                target_domain = parsed_target_url.netloc

                # if there is a www, lets remove it
                if target_domain.startswith('www.'):
                    target_domain = target_domain[4:]

                # we need a regexp to search for strings that contain
                # either 1) target domain 2) a "/{path}"
                internal_link_regexp = re.compile(
                    r'(^/|https?://(www.)?{domain})'.format(domain=target_domain))

                mo = internal_link_regexp.match(link_href)

                # if the path contains the target domain, or is a "/{path}"
                if mo and mo.group():

                    # let's filter out any pdf links
                    pdf_link_regexp = re.compile(
                        r'(.pdf)$')

                    mo = pdf_link_regexp.search(link_href)

                    # if there is no match object, the href isn't a pdf link
                    if mo is None:

                        # lets push it to our valid internal links
                        valid_internal_links.append(link_href)

    else:
        # if no links were found on the page, bail!
        return False

    # if there were links found on the page, lets return them
    return valid_internal_links


def extract_page_title_as_text(html_soup: BeautifulSoup):
    # let's extract the pages <title> tag with BeautifulSoup
    html_page_title = html_soup.head.title.string
    return html_page_title + "\n"


def extract_body_content_as_text(html_soup: BeautifulSoup):
    # let's extract the text from the <body> with BeautifulSoup
    html_body_text_content = html_soup.body.get_text()
    return html_body_text_content + "\n"


def extract_and_format_main_content_as_text(html_soup: BeautifulSoup):
    main_content = []

    for tag in html_soup.find_all(re.compile('^(h[1-6]|p)')):
        tag_text = tag.get_text()

        if tag_text not in main_content:
            main_content.append(tag_text + "\n")

    main_content_text = "\n".join(main_content)

    print(main_content_text)

    return main_content_text


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content
