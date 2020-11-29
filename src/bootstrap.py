import os
import ssl

# we need to set the deafult sll context to 'unverified'
# not okay for production code!!!
# if prod: use requests module instead


def set_ssl_context():
    ssl._create_default_https_context = ssl._create_unverified_context


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
