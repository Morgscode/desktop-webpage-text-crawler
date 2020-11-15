import sys

import src.bootstrap as bootstrap
import src.location_handler as location_handler
import src.web_scraper as web_scraper
import src.file_handler as file_handler

from urllib.request import urlopen, URLError
from urllib.error import HTTPError
from urllib.parse import urlparse

from tkinter import *

window = Tk()

# website field label
domain = StringVar()
domain_label = Label(
    window, text="Enter the website url you want to index", font=("bold", 16), padx=50, pady=10)
domain_label.grid(row=1, column=0, sticky=W)

# website text field
domain_entry = Entry(window, textvariable=domain)
domain_entry.grid(row=2, column=0, ipady=5, ipadx=5)

# button function


def grab_webpage_content():
    global domain

    target_url = domain.get()

    bootstrap.set_ssl_context()

    # let's run it through our validation function
    location_handler.validate_web_url(target_url)

    # if validation passes, parse the url
    parsed_target_url = urlparse(target_url)

    bootstrap.setup_file_system(parsed_target_url)

    # let's get the url as html
    html = web_scraper.get_webpage_html(target_url)

    if html is None:
        # if the url opens, but there is no response, exit
        sys.exit('invalid domain given! check the logs....')

    # convert into beautifulsoup object
    html_soup = web_scraper.convert_html_to_soup_obj(html, target_url)

    # let's extract the links in the nav element
    webpage_links = web_scraper.get_webpage_links_in_nav(html_soup)

    # we'll use enumerate to generate an scope specific index
    # this is used in the write file functions
    for index, link in enumerate(webpage_links):

        page_html = web_scraper.get_webpage_html(link)

        page_html_soup = web_scraper.convert_html_to_soup_obj(
            page_html, target_url)

        page_html_text_content = web_scraper.convert_soup_to_text(
            page_html_soup)

        formatted_path = location_handler.format_path(link)

        new_file_loaction = file_handler.write_text_to_file(
            page_html_text_content, formatted_path, index, parsed_target_url)

        formatted_text = file_handler.strip_whitespace_from_file(
            new_file_loaction)

        file_handler.write_text_to_file(
            formatted_text, formatted_path, index, parsed_target_url)

        domain_entry.delete(0, 'end')


# button
crawl_button = Button(window, text="Get website content",
                      font=14, command=grab_webpage_content)
crawl_button.grid(row=3, column=0, pady=10, ipadx=12, ipady=7)

window.title('Webpage content scraper')
window.geometry('400x200+250+200')

window.mainloop()

# bye :)
sys.exit('done scraping! going to sleep now....')
