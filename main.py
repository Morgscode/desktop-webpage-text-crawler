import sys

import src.bootstrap as bootstrap
import src.location_handler as location_handler
import src.web_scraper as web_scraper
import src.file_handler as file_handler

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse

from tkinter import *
from tkinter import messagebox


def retrieve_and_parse_url():
    target_url = domain.get()
    formatted_target_url = location_handler.manage_domain_scheme(target_url)
    parsed_target_url = urlparse(formatted_target_url)
    return parsed_target_url


def validate_domain_or_fail(url: str):
    try:
        # let's run it through our validation function
        location_handler.validate_web_url(url)

    except:
        # this will catch invalid domains, we'll write to logs and return false
        error = "Web-scraper error in main.py: validate_domain_or_fail fn...the domain: {target_url} is NOT valid\n".format(
            target_url=url)

        with open("./web-scraper-logs/error.txt", "a+") as error_file:
            error_file.write(error)

        return False
    else:
        return True


def init():
    target_url = domain.get()

    formatted_target_url = location_handler.manage_domain_scheme(target_url)

    bootstrap.setup_error_logs()

    bootstrap.set_ssl_context()

    res = validate_domain_or_fail(formatted_target_url)

    if res:
        # if validation passes, parse the url
        parsed_target_url = urlparse(formatted_target_url)
        # create a directory for the data
        bootstrap.setup_data_directory(parsed_target_url)

    return res


def index_webpage_content_by_url(link, index):

    # let's grab the html response from the server
    page_html = web_scraper.get_webpage_html(link)

    # let's conver it to some tasty soup
    page_html_soup = web_scraper.convert_html_to_soup_obj(
        page_html)

    # extract the text from this page
    page_html_text_content = web_scraper.convert_soup_to_text(
        page_html_soup)

    # let's generate a formatted path for this webpage
    formatted_path = location_handler.format_path_as_file_location(link)

    # we'll also need a parse version of the full url
    parsed_target_url = retrieve_and_parse_url()

    # let's write the retieved text to a file and get it's location
    # the index will be 0 or more, this will order the files
    new_file_loaction = file_handler.write_text_to_file(
        page_html_text_content, formatted_path, index, parsed_target_url)

    # let's strip all of the unneede whitespace, and tidy it up
    formatted_text = file_handler.strip_whitespace_from_file(
        new_file_loaction)

    # let's rewrite the cleaned text to the file
    file_handler.write_text_to_file(
        formatted_text, formatted_path, index, parsed_target_url)


def process_user_crawl_request():

    has_initialized = init()

    if has_initialized:

        target_url = domain.get()

        formatted_target_url = location_handler.manage_domain_scheme(
            target_url)

        # let's get the url as html
        html = web_scraper.get_webpage_html(formatted_target_url)

        if html is None:
            domain_entry.delete(0, 'end')
            # if the url opens, but there is no response, bail
            return False
        else:
            # convert into beautifulsoup object
            html_soup = web_scraper.convert_html_to_soup_obj(html)

            # let's extract the links in the nav element
            webpage_links_in_navs = web_scraper.get_valid_webpage_link_hrefs_in_navs(
                html_soup)

            formatted_webpage_links_in_nav = []

            for webpage_link_href in webpage_links_in_navs:
                webpage_link_href = location_handler.format_href_as_url(
                    webpage_link_href, formatted_target_url)
                formatted_webpage_links_in_nav.append(webpage_link_href)

            if len(formatted_webpage_links_in_nav) > 0:
                # we'll use enumerate to generate an scope specific index
                # this is used in the write file functions
                pages_indexed = 0

                for index, link in enumerate(formatted_webpage_links_in_nav):
                    try:
                        index_webpage_content_by_url(link, index)
                    except:
                        # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                        error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT valid\n".format(
                            target_url=link)

                        with open("./web-scraper-logs/error.txt", "a+") as error_file:
                            error_file.write(error)

                    else:
                        pages_indexed += 1

                domain_entry.delete(0, 'end')

                messagebox.showinfo(title="great success!", message="done scraping! - crawled {crwl_pg_count} pages, indexed {ind_pg_count}... ready for more".format(
                    crwl_pg_count=len(formatted_webpage_links_in_nav), ind_pg_count=pages_indexed))

            else:
                try:
                    # if there are no links in a nav, just index the content on that page
                    index_webpage_content_by_url(target_url, 0)
                except:
                    # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                    error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT valid\n".format(
                        target_url=target_url)

                    with open("./web-scraper-logs/error.txt", "a+") as error_file:
                        error_file.write(error)

                domain_entry.delete(0, 'end')

                messagebox.showinfo(
                    title="great success!", message="done scraping! - indexed 1 page... ready for more")

    else:
        # if init() returns false, we've handled it
        # so just clear the gui input
        messagebox.showinfo(title="Invalid domain requested",
                            message="That domain was invalid, check the logs for more information.")


# lets build the gui
window = Tk()

window.title('Webpage content scraper')
window.geometry('400x200+250+200')

# website field label
domain = StringVar()
domain_label = Label(
    window, text="Enter the website url you want to index", font=("normal", 18))
domain_label.grid(row=1, sticky=W, padx=3, pady=5)

# website text field
domain_entry = Entry(window, textvariable=domain)
domain_entry.grid(row=2, sticky=W, padx=5, pady=5)

# button
crawl_button = Button(window, text="Get website content",
                      font=14, command=process_user_crawl_request)
crawl_button.grid(row=3, sticky=W,  padx=5, pady=5)

# run the gui
window.mainloop()

# bye :)
sys.exit('done scraping! going to sleep now....')
