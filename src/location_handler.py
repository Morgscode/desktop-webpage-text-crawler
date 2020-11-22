import sys

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse


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


# we need an fn to ensure there is a http shceme and domain name for each link href
# we'll need a regexp to check for these, and add them if none
def format_href_as_url(href: str, target_domain):
    # let's only push urls that are valid, and havn't been indexed in this fn
    # this regexp will pick up 'tel:, mailto: and #' hrefs
    href_regexp = re.compile(
        r'(https?://)(www.)?(.*)+')

    mo = page_link_regexp.search(href)

    parsed_target_domain = urlparse(target)

    print(parsed_target_domain)

    if mo is None:
        # let's strip any trailing slashes
        if href[0] == "/":
            href = href[1:]
        # if there wasn't shceme or url found
        href = "{scheme}{domain}{href}".format(
            scheme=parsed_target_domain.scheme, domain=parsed_target_domain.netloc)

        return href
    else:
        return href
