# packages = { BeautifulSoup: html-parsing }
# This script will index all of the text content on webapges found within the NAV element of a website
# pass the website you want to index in the target_url variable on line 15

import ssl
import sys
import os

from urllib.request import urlopen, URLError
from urllib.error import HTTPError
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# this will be the url which will evetually be given by the gui
target_url = "https://kumi-solutions.com"

# we need to set the deafult sll context to 'unverified'
# not okay for production code!!!
ssl._create_default_https_context = ssl._create_unverified_context

# let's create a directory for logs
if not os.path.exists('./web-scraper-logs'):
    os.makedirs('./web-scraper-logs')


def validate_web_url(url: str):
    # let's define a function to validate a url
    # on fail, we'll write to logs and exit
    global target_url
    try:
        urlopen(target_url)
        return True
    except URLError as e:
        error = "Web-scraper error at line 29... error reason is: {errreason}\n".format(
            errreason=e.reason)
        error_file = open("./web-scraper-logs/error.txt", "a+")
        error_file.write(error)
        error_file.close()
        sys.exit("invalid url at line 20! shutting down...")


validate_web_url(target_url)

# if validation passes, parse the url
parsed_target_url = urlparse(target_url)

# let's create a directory for data
if not os.path.exists('./web-scraper-data/' + str(parsed_target_url.netloc)):
    os.makedirs('./web-scraper-data/' + str(parsed_target_url.netloc))


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
    global target_url

    if html is None:
        print('There was no data found at that url')
        error = "There was no data found at " + str(target_url) + "\n"
        error_file = open("./web-scraper-logs/error.txt", "a")
        error_file.write(error)
        error_file.close()
        return
    else:
        # lets store the html as a utf-8 encoded string
        html_string = html.read().decode('utf-8')

        # let's parse the html into an object with BeautifulSoup
        html_soup = BeautifulSoup(html_string, 'html.parser')

        return html_soup


def get_webpage_links_in_nav(html: BeautifulSoup):
    links = []
    for link in html.nav.find_all('a'):
        page_link = link.get('href')
        links.append(page_link)

    return links


def convert_soup_to_text(html_soup: BeautifulSoup):
    # let's extract the text with BeautifulSoup
    html_text_content = html_soup.get_text()
    return html_text_content


def format_path(link: str):
    parsed_url = urlparse(link)
    file_path = parsed_url.path

    # let's check to see if there is a path, or if the path is a backslash and rename it index
    if file_path == "/" or not file_path:
        file_path = "index"

    # next we need to strip away any trailing slashes
    if file_path[0] == "/":
        file_path = file_path[1:]

    if file_path[-1] == "/":
        file_path = file_path[:-1]

    # if there is a slash anywhere in the path, let's split the string by the slashes and take the final path parameter
    if "/" in file_path:
        file_pathList = file_path.split("/")
        file_path = file_pathList[-1]

    return file_path


def write_text_to_file(web_page_text: str, formatted_path: str,  counter: int):
    global parsed_target_url
    text_file_location = "./web-scraper-data/{domain}/{pgindex}_{fmtdpath}.txt".format(
        domain=parsed_target_url.netloc, pgindex=str(counter), fmtdpath=formatted_path)
    # lets open/create a new file called in the website data directory and overwrite its contents if its been indexed before
    # we use the counter to map the files in the directory to the same cacnonical order as the nav
    text_file = open(text_file_location, "w")

    # lets write the text content to the new file we created
    text_file.write(web_page_text)

    # all done, close the file stream
    text_file.close()

    return text_file_location


def strip_whitespace_from_file(text_file: str):
    stripped_text = []

    with open(text_file, "r") as parsed_text_file:
        for line in parsed_text_file:
            line = line.rstrip().lstrip()
            if line:
                stripped_text.append(line)

    formatted_text_content = "\n".join(stripped_text)

    return formatted_text_content

    # let's get the url as html
html = get_webpage_html(target_url)

if html is None:
    # if the url opens, but there is no response, exit
    sys.exit('invalid domain given! check the logs....')

# convert into beautifulsoup object
html_soup = convert_html_to_soup_obj(html)

# let's extract the links in the nav element
webpage_links = get_webpage_links_in_nav(html_soup)

# we'll use enumerate to generate an scope specific index
# this is used in the write file functions
for index, link in enumerate(webpage_links):
    page_html = get_webpage_html(link)
    page_html_soup = convert_html_to_soup_obj(page_html)
    page_html_text_content = convert_soup_to_text(page_html_soup)
    formatted_path = format_path(link)
    new_file_loaction = write_text_to_file(
        page_html_text_content, formatted_path, index)
    formatted_text = strip_whitespace_from_file(new_file_loaction)
    write_text_to_file(formatted_text, formatted_path, index)

# bye :)
sys.exit('done scraping! going to sleep now....')
