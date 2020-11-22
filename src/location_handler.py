import sys
import re

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse


def manage_domain_scheme(target_domain: str):
    # we need a function to add a scheme to the url is one if not present.
    # this regexp will check for a scheme
    scheme_regexp = re.compile(r'https?://')

    mo = scheme_regexp.search(target_domain)
    # if no match is found, let's attach a default http:// scheme
    if mo is None:
        target_domain = "http://{domain}".format(domain=target_domain)

    return target_domain


def validate_web_url(url: str):
    # let's define a function to validate a url
    try:
        response = urlopen(url)
    except HTTPError as e:
        # this will catch 404s, 500s etc, we'll write to logs and exit
        error = "Web-scraper error in vaidate_web_url fn... ECODE: {errcode} error reason is: {errreason}\n".format(
            errcode=e.code, errreason=e.reason)

        with open("./web-scraper-logs/error.txt", "a+") as error_file:
            error_file.write(error)

        return False
    else:
        return True


def format_path(link: str):
    # let's parse the url and grab the path
    parsed_url = urlparse(link)
    file_path = parsed_url.path

    # let's check to see if there is a path, or if the path is a backslash and rename it index
    if file_path == "/" or not file_path:
        file_path = "index"

    # next we need to strip away any leading or trailing slashes
    if file_path[0] == "/":
        file_path = file_path[1:]

    if file_path[-1] == "/":
        file_path = file_path[:-1]

    # if there is a slash anywhere in the path, let's split the string by the slashes and take the final pathname
    if "/" in file_path:
        file_pathList = file_path.split("/")
        file_path = file_pathList[-1]

    return file_path


def format_href_as_url(href: str, target_domain: str):

    # if the href is "/", it's valid
    if href != "/":
        # if its longer
        while href[0] == "/":
            # strip away any leading slashes
            href = href[1:]

        # we'll need a regexp to check for hrefs that arent valid
        # if there is a https:// or www. at the beginning, we'll need
        # to run some extra checks
        href_regexp = re.compile(
            r'((https?://)|(www.))(.*)+')

        mo = href_regexp.match(href)

        if mo:
            # let's asses for either a www. or no scheme
            if mo.group() and re.match(r'www.', mo.group()) or mo.group() and not re.match(r'https?://', mo.group()):
                # let's parse the target_domain to use it to format
                # an incorecct href into a url
                parsed_target_domain = urlparse(target_domain)
                # if there wasn't shceme found
                href = "{scheme}://{href}".format(
                    scheme=parsed_target_domain.scheme, href=href)
                return href
            else:
                # if the href is a valid url, just return it
                return href
    else:
        # if the href was "/", return it
        return href
