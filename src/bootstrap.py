import os
import ssl


def setup_data_directory(parsed_target_url):
    # let's create a directory for data
    if not os.path.exists('./web-scraper-data/' + str(parsed_target_url.netloc)):
        os.makedirs('./web-scraper-data/' + str(parsed_target_url.netloc))


def setup_error_logs():
    # let's create a directory for logs
    if not os.path.exists('./web-scraper-logs'):
        os.makedirs('./web-scraper-logs')


def dir_exists(dir: str):
    if not os.path.exists(dir):
        return False
    else:
        return True
