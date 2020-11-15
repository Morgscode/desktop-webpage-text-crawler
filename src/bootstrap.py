import os
import ssl

# we need to set the deafult sll context to 'unverified'
# not okay for production code!!!


def set_ssl_context():
    ssl._create_default_https_context = ssl._create_unverified_context


def setup_file_system(parsed_target_url):
    # let's create a directory for logs
    if not os.path.exists('./web-scraper-logs'):
        os.makedirs('./web-scraper-logs')

    # let's create a directory for data
    if not os.path.exists('./web-scraper-data/' + str(parsed_target_url.netloc)):
        os.makedirs('./web-scraper-data/' + str(parsed_target_url.netloc))
