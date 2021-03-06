import sys
import time

import src.bootstrap as bootstrap
import src.location_handler as location_handler
import src.web_scraper as web_scraper
import src.file_handler as file_handler

from urllib.parse import urlparse

from tkinter import *
from tkinter import messagebox, filedialog


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


def open_data_dir():
    is_dir = bootstrap.dir_exists("./web-scraper-data")

    if is_dir:
        filedialog.askopenfilename(
            initialdir="./web-scraper-data", title="Browse your scraped websites")
    else:
        messagebox.showerror(title="oops! we couldn't find the data folder",
                             message="it looks that folder doesn't exist, try crawling a site first...")


def open_logs_dir():
    is_dir = bootstrap.dir_exists("./web-scraper-logs")

    if is_dir:
        filedialog.askopenfilename(
            initialdir="./web-scraper-logs", title="Browse the crawlers error logs")
    else:
        messagebox.showerror(title="oops! we couldn't find the logs",
                             message="it looks like that folder doesn't exist, try crawling a site first...")


def init():
    target_url = domain.get()

    formatted_target_url = location_handler.manage_domain_scheme(target_url)

    bootstrap.setup_error_logs()

    res = validate_domain_or_fail(formatted_target_url)

    if res:
        # if validation passes, parse the url
        parsed_target_url = urlparse(formatted_target_url)
        # create a directory for the data
        bootstrap.setup_data_directory(parsed_target_url)

    return res


def show_url_crawl_error(target_url: str):
    messagebox.showerror(title="oh dear! there was an issue",
                         message="there was a problem when crawling {target_url}... check the logs for information".format(target_url=target_url))


def show_single_page_success():
    messagebox.showinfo(
        title="great success!", message="done scraping! - indexed 1 page... ready for more")


def show_user_crawl_option(option: str):
    # for testing the options button
    print(crawl_option.get())


def show_user_content_option(option: str):
    # for testing the options button
    print(content_option.get())


def index_webpage_content_by_url(link: str, index: int):

    # let's grab the html response from the server
    page_html = web_scraper.get_webpage_html(link)

    response_is_text_or_json = web_scraper.assess_content_type_for_text_or_json(
        page_html)

    if not response_is_text_or_json:
        return False

    # let's conver it to some tasty soup
    page_html_soup = web_scraper.convert_html_to_soup_obj(
        page_html)

    user_content_option = content_option.get()

    if user_content_option == 'page title':
        # extract the page title
        page_html_text_content = web_scraper.extract_page_title_as_text(
            page_html_soup)

    elif user_content_option == 'main content':
        # extract the page's main content
        page_html_text_content = web_scraper.extract_and_format_main_content_as_text(
            page_html_soup)

    elif user_content_option == 'all content':
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

    ###
    # errors need to be allowed to continue in this function
    # so it can complete, regardless of state and give the
    # user some feedback... this maintains the ux
    # if errors do occur...
    # errors WILL be written to the logs
    # error messages WILL be displayed to the user
    ###

    ###
    # indexing all webpage links
    # in a nav or on the page can
    # turn into a really expensive
    # function.
    # so we introduce a 1 second
    # crawl delay in those loops.
    # This benefits us, and the
    # domain's server
    ###

    has_initialized = init()

    target_url = domain.get()

    if has_initialized:

        formatted_target_url = location_handler.manage_domain_scheme(
            target_url)

        # let's get the url as html
        html = web_scraper.get_webpage_html(formatted_target_url)

        if html.status_code != 200:
            show_url_crawl_error(formatted_target_url)

            return False

        # convert into beautifulsoup object regardsless of response
        html_soup = web_scraper.convert_html_to_soup_obj(html)

        user_crawl_option = crawl_option.get()

        if user_crawl_option == 'single page':

            try:
                index_webpage_content_by_url(formatted_target_url, 0)
                show_single_page_success()
            except:
                # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT indexable as text content\n".format(
                        target_url=target_url)

                with open("./web-scraper-logs/error.txt", "a+") as error_file:
                    error_file.write(error)

                # show the user an error message for single page indexing blocks
                show_url_crawl_error(formatted_target_url)

            # once we're done, clear the form entry
            domain_entry.delete(0, 'end')

        elif user_crawl_option == 'navigation links':

            # let's extract the links in the nav element
            webpage_links_in_navs = web_scraper.get_valid_webpage_link_hrefs_in_navs(
                html_soup)

            # let's create an empty list to collect formatted hrefs
            formatted_webpage_links_in_nav = []

            # let's loop over our unformatted hrefs
            for webpage_link_href in webpage_links_in_navs:

                # format or return None
                webpage_link_href = location_handler.format_href_as_url(
                    webpage_link_href, formatted_target_url)
                formatted_webpage_links_in_nav.append(webpage_link_href)

            if len(formatted_webpage_links_in_nav) > 0:
                # these counters are used in the write file feedback
                pages_indexed = 0
                indexing_errors = 0

                # lets grab the page we requested before indexing the nav
                index_webpage_content_by_url(formatted_target_url, 0)

                for index, link in enumerate(formatted_webpage_links_in_nav):
                    # we'll use enumerate to generate an scope specific index
                    try:
                        index_webpage_content_by_url(link, index + 1)
                        # lets sleep for a second to introduce a crawl delay
                        time.sleep(1)
                    except:
                        # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                        error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT valid\n".format(
                                target_url=link)

                        with open("./web-scraper-logs/error.txt", "a+") as error_file:
                            error_file.write(error)
                            # lets sleep for a second to introduce a crawl delay
                            time.sleep(1)

                        indexing_errors += 1

                    else:
                        # if the try block carried: add 1 to our index coutner
                        pages_indexed += 1

                domain_entry.delete(0, 'end')

                # give the user some feedback
                messagebox.showinfo(title="great success!", message="done scraping! - crawled {crwl_pg_count} pages, indexed {ind_pg_count} pages with {error_count} errors... ready for more".format(
                    crwl_pg_count=len(formatted_webpage_links_in_nav), ind_pg_count=pages_indexed, error_count=indexing_errors))

            else:
                try:
                    # if there are no links in a nav, just index the content on that page
                    index_webpage_content_by_url(formatted_target_url, 0)
                    show_single_page_success()
                except:
                    # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                    error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT indexable as text content\n".format(
                            target_url=formatted_target_url)

                    with open("./web-scraper-logs/error.txt", "a+") as error_file:
                        error_file.write(error)

                    show_url_crawl_error(formatted_target_url)

                domain_entry.delete(0, 'end')

        elif user_crawl_option == 'internal page links':

            # let's extract the links in the nav element
            internal_page_links = web_scraper.get_internal_links_from_webpage(
                html_soup, formatted_target_url)

            formatted_internal_webpage_links = []

            for webpage_link_href in internal_page_links:
                webpage_link_href = location_handler.format_href_as_url(
                    webpage_link_href, formatted_target_url)
                formatted_internal_webpage_links.append(webpage_link_href)

            if len(formatted_internal_webpage_links) > 0:
                # we'll use enumerate to generate an scope specific index
                # this is used in the write file functions
                pages_indexed = 0
                indexing_errors = 0

                # if there are no links in a nav, just index the content on that page
                index_webpage_content_by_url(formatted_target_url, 0)

                for index, link in enumerate(formatted_internal_webpage_links):
                    try:
                        index_webpage_content_by_url(link, index + 1)
                        # lets sleep for a second to introduce a crawl delay
                        time.sleep(1)
                    except:
                        # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                        error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT valid\n".format(
                                target_url=link)

                        with open("./web-scraper-logs/error.txt", "a+") as error_file:
                            error_file.write(error)
                            # lets sleep for a second to introduce a crawl delay
                            time.sleep(1)

                        indexing_errors += 1
                    else:
                        pages_indexed += 1

                domain_entry.delete(0, 'end')

                messagebox.showinfo(title="great success!", message="done scraping! - crawled {crwl_pg_count} pages, indexed {ind_pg_count} pages with {error_count} errors... ready for more".format(
                    crwl_pg_count=len(formatted_internal_webpage_links), ind_pg_count=pages_indexed, error_count=indexing_errors))

            else:
                try:
                    # if there are no links in a nav, just index the content on that page
                    index_webpage_content_by_url(formatted_target_url, 0)
                    show_single_page_success()
                except:
                    # this will catch invalid links which aren't yet filtered, we'll write to logs and allow the program to continure
                    error = "Web-scraper error in main.py: index_webpage_content_by_url fn...the domain: {target_url} is NOT indexable as text content\n".format(
                        target_url=formatted_target_url)

                    with open("./web-scraper-logs/error.txt", "a+") as error_file:
                        error_file.write(error)

                    show_url_crawl_error(formatted_target_url)

                domain_entry.delete(0, 'end')

    else:
        # if init() returns false, we've handled it
        # so just show user the error but dont clear the input
        show_url_crawl_error(target_url)


# lets build the gui
window = Tk()

window.title('Webpage content scraper')
window.geometry('450x450+250+200')
window.configure(bg="#CFD8DC")

# set up the frame for the domain entry widget field
domain_entry_frame = Frame(window, width=100, height=100, bg="#455A64")
domain_entry_frame.grid(sticky=NSEW, column=0,
                        columnspan=4, ipady=10, ipadx=10)
domain_entry_frame.grid_columnconfigure(0, weight=1)

# website field var
domain = StringVar()

# set up the label widget and position in grid
domain_label = Label(
    domain_entry_frame, text="Enter the website url you want to index:", font=("normal", 18), bg="#455A64", fg="#212121")
domain_label.grid(row=1, sticky=W, padx=5, pady=5, columnspan=4)

# website text field
domain_entry = Entry(domain_entry_frame,
                     textvariable=domain)
domain_entry.configure(bg="#CFD8DC", border=0)
domain_entry.grid(row=2, sticky=EW, padx=5, pady=5,
                  ipady=5, ipadx=10,  columnspan=1)
domain_entry.grid_columnconfigure(0, weight=1)

# set up the frame for crawl options
crawl_options_frame = Frame(window, width=100, height=100, bg="#607D8B")
crawl_options_frame.grid(row=1, sticky=NSEW, column=0,
                         columnspan=4, ipady=10, ipadx=10)
crawl_options_frame.grid_columnconfigure(0, weight=1)

# lets store the crawl option
crawl_option = StringVar()

# define the crawl options
crawl_options = [
    'single page',
    'navigation links',
    'internal page links',
]

# crawl options variable
crawl_option.set(crawl_options[0])

# crawl options variable label
crawl_option_label = Label(
    crawl_options_frame, text="Refine how you crawl the domain:", font=("normal", 14), bg="#607D8B", fg="#212121")
crawl_option_label.grid(row=0, sticky=W, padx=5, pady=5)

# crawl options menu
crawl_option_menu = OptionMenu(crawl_options_frame, crawl_option, *crawl_options,  # command=show_user_crawl_option
                               )
crawl_option_menu.configure(bg="#607D8B", fg="#212121")
crawl_option_menu.grid(row=1, padx=5, pady=5, sticky=EW)

# set a variable for content options
content_option = StringVar()

# define the content options
content_options = [
    'main content',
    'all content',
    'page title',
]

# crawl options variable
content_option.set(content_options[0])

# create a label for the content option
content_option_label = Label(
    crawl_options_frame, text="Select content to index:", font=("normal", 14), bg="#607D8B", fg="#212121")
content_option_label.grid(row=2, sticky=W, padx=5, pady=5)

# crawl options menu
content_option_menu = OptionMenu(crawl_options_frame, content_option, *content_options,   command=show_user_content_option
                                 )
content_option_menu.configure(bg="#607D8B", fg="#212121")
content_option_menu.grid(row=3, padx=5, pady=5, sticky=EW)

# set up the frame for the crawl button
crawl_button_frame = Frame(window, width=100, height=100, bg="#CFD8DC")
crawl_button_frame.grid(row=2, sticky=NSEW, column=0, columnspan=4)
crawl_button_frame.grid_columnconfigure(0, weight=1)

# crawl button
crawl_button = Button(crawl_button_frame, text="Get website content",
                      font=14, command=process_user_crawl_request)
crawl_button.configure(border=0, pady=10, fg="#212121", bg="#757575")
crawl_button.grid(sticky=EW, padx=5, pady=10)

# a frame for the directory dialouge buttons
dir_buttons_frame = Frame(window, width=100, height=100, bg="#CFD8DC")
dir_buttons_frame.grid(row=3, sticky=NSEW, columnspan=4)
dir_buttons_frame.grid_columnconfigure(0, weight=1)

# data directory button
data_dir_button = Button(dir_buttons_frame, text="Open data folder",
                         font=14, command=open_data_dir)
data_dir_button.configure(padx=5, pady=5, fg="#212121", bg="#757575")
data_dir_button.grid(sticky=W, padx=5, pady=10)

# error logs directory button
error_logs_dir_button = Button(dir_buttons_frame, text="Open logs",
                               font=14, command=open_logs_dir, )
error_logs_dir_button.configure(padx=5, pady=5, fg="#212121", bg="#757575")
error_logs_dir_button.grid(row=0, padx=5, pady=5)

# run the gui
window.mainloop()

# bye :)
sys.exit('done scraping! going to sleep now....')
