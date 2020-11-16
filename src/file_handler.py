def write_text_to_file(web_page_text: str, formatted_path: str,  counter: int, parsed_target_url: str):
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
            # let's strip all of the leading and trailing whitespace from each line
            line = line.rstrip().lstrip()
            # if the line of text isn't empty, push to our return value
            if line:
                stripped_text.append(line)

    # let's join the array into a string, seperating each element with a new link
    formatted_text_content = "\n".join(stripped_text)

    return formatted_text_content
