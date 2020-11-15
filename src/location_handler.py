import sys

from urllib.request import urlopen, URLError
from urllib.parse import urlparse


def validate_web_url(url: str):
    # let's define a function to validate a url
    # on fail, we'll write to logs and exit
    try:
        urlopen(url)
        return True
    except URLError as e:
        error = "Web-scraper error at line 29... error reason is: {errreason}\n".format(
            errreason=e.reason)
        error_file = open("./web-scraper-logs/error.txt", "a+")
        error_file.write(error)
        error_file.close()
        sys.exit("invalid url at line 20! shutting down...")


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
