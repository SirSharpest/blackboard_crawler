################################################
# This is a simple application that will hopefully
# grab pdf's from blackboard and store them on your machine
################################################


################################################
# Imports
################################################
import os
import urllib.request
import http.cookiejar
from os.path import expanduser
import time
import getpass
import urllib.request
import urllib.parse
import bs4
from mimetypes import guess_extension
from documents import pdfFile, bbFolder
from HeadHTTPRedirectHandler import HeadHTTPRedirectHandler, HeadRequest
import re
import sys
import getopt

################################################
# Functions
###############################################


def login_bb(user_id, user_passwd):

    authentication_url = 'https://blackboard.aber.ac.uk/webapps/login/'

    payload = {
        'op': 'login',
        'user_id': user_id,
        'password': user_passwd
    }

    print('Entering Blackboard...')

    data = urllib.parse.urlencode(payload)
    binary_data = data.encode('UTF-8')
    req = urllib.request.Request(authentication_url, binary_data)
    resp = urllib.request.urlopen(req)
    contents = resp.read()

    print('Connected!\n')


# Does just that, finds a file pdf,ppt or pptx and saves it
def download_file(file_to_get):

    if os.path.isfile(file_to_get.get_name()):
        print(file_to_get.get_name() +
              " already exists in this directory... skipping it")
        return
    else:
        try:
            print('Accessing: ' + file_to_get.get_name())
            source = urllib.request.urlopen(file_to_get.get_url())
            app_name = file_to_get.get_name().encode('utf-8')
            file = open(app_name, 'wb')
            file.write(source.read())
            file.close()
            print('File saved: ' + file_to_get.get_name())
        except:
            print("Couldn't get the file... possible 404 error")


def convert_relative_to_absolute_url(url):

    # Returns the converted absolute BB url, or returns the original URL
    # unmodified.
    return re.sub(r'^(\/.*)$', r'https://blackboard.aber.ac.uk\1', url)


def resolve_redirected_url(originalURL):

    # If we have a new URL from the response, return that.
    # Otherwise return the original URL.
    try:

        opener = urllib.request.OpenerDirector()

        for handler in [urllib.request.HTTPHandler,
                        urllib.request.HTTPDefaultErrorHandler,
                        urllib.request.HTTPErrorProcessor,
                        urllib.request.HTTPSHandler,
                        HeadHTTPRedirectHandler]:

            opener.add_handler(handler())

        response = opener.open(HeadRequest(originalURL))

        return response.geturl()

    except:
        return originalURL


def is_supported_file_url(fileURL):

    file_url_match = re.search(r'^(https?\:\/\/blackboard.aber.ac.uk).*\.((?:doc|xls|ppt)x?|pdf|txt|class|zip)$',
                               fileURL.lower())
    return file_url_match


def extract_filename_from_url(fileURL):

    url_parts = urllib.parse.urlparse(fileURL)
    path_parts = url_parts[2].rpartition('/')
    return path_parts[2]

# This will print the links which have "pdf" specified in the naming


def get_links(url, folderName):

    try:

        site = urllib.request.urlopen(url)
        html = site.read()
        # parse the html
        soup = bs4.BeautifulSoup(html, 'html.parser')

        data = soup.find_all(id='content_listContainer')

        # container for the docs
        documents = []

        for div in data:

            links = div.find_all('a')

            for a in links:

                # We need to make sure all URLs that we wish to inspect are absolute in
                # order to resolve any redirected URLs.
                absolute_href_url = convert_relative_to_absolute_url(a['href'])

                # In order to check whether or not a BB file is accessible, we need
                # to perform a HTTP HEAD request in order to resolve any
                # redirects.
                redirect_url = resolve_redirected_url(absolute_href_url)

                # We currently support only a specific set of URL domains and
                # file extensions.
                if is_supported_file_url(redirect_url):

                    try:

                        temp_doc = pdfFile()

                        # On some occasions weird filenames can appear if we just use the
                        # title of the link from BB itself. Therefore we should instead use
                        # the ACTUAL filename (inc. correct extension) directly
                        # from the file URL.
                        file_name = extract_filename_from_url(redirect_url)

                        print("  - File found: " + file_name)

                        temp_doc.set_name(file_name)
                        temp_doc.set_url(redirect_url)

                        documents.append(temp_doc)

                    except:
                        print("Error whilst trying to get the address of a file")
                        continue

        return documents

    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        # raise MyException("There was an error: %r" % e)
        print("Likely timeout error. Continuing.")

        return []


def get_folder_links(url, divtag):
    site = urllib.request.urlopen(url)
    html = site.read()

    # parse the html
    soup = bs4.BeautifulSoup(html, 'html.parser')

    data = soup.find_all(id=divtag)

    # container for the docs
    documents = []

    for div in data:
        links = div.find_all('a')
        for a in links:
            try:
                if 'listContent' in a['href'] or 'execute' in a['href']:

                    folder = bbFolder()
                    folder.set_name(a.text)

                    if '/' in folder.get_name():
                        folder.set_name(folder.get_name().replace('/', ' '))
                        # fixes bug of its making extra folder
                        folder.set_name(
                            str(folder.get_name()).replace('/', '\\'))

                    folder.set_url(convert_relative_to_absolute_url(a['href']))

                    if "listContentEditable" in a['href']:
                        continue

                    if divtag == 'module:_371_1':
                        # REGEX checks for module code patterns matching EITHER 'AB12345' or 'ABC1234' (case-insensitive).
                        # Some modules (e.g. Masters) use three letters and
                        # four numbers, rather than two letters and five
                        # numbers.
                        module_pattern = re.compile(
                            '[a-zA-Z]{2}\d{5}|[a-zA-Z]{3}\d{4}')
                        if module_pattern.search(a.text) is not None:
                            print('Found Module: ' + a.text)
                            documents.append(folder)
                        continue

                    documents.append(folder)

                if "launchLink" in a['href']:
                    continue
            except:
                print("Oh deer, something broke whilst finding folder links")
                continue

    return documents


# This function should get all of the links in the sidebar
def find_content_link(url):
    site = urllib.request.urlopen(url)
    html = site.read()

    # parse the html
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # data = soup.find_all(id='content')
    data = soup.find_all(id='courseMenuPalette_contents')

    content = []

    links = data[0].find_all('a')
    for a in links:
        # somethings we want to ignore
        if "panopto" in a.span.text.lower() or "announcements" in a.span.text.lower() or "discussion" \
                in a.span.text.lower() or "aspire" in a.span.text.lower() or "tools" in a.span.text.lower() \
                or "http" in a.text.lower():
            continue

        if "content"  in a.span.text.lower() or "slides" in a.span.text.lower() \
                or "course" in a.span.text.lower() or "lecture" in a.span.text.lower():

            folder = bbFolder()
            folder.set_name(a.span.text)

            folder.set_url(convert_relative_to_absolute_url(a['href']))

        else:
            continue

        content.append(folder)

    return content


def get_all_folders(startFolder):

    print("\nDirectory found: " + startFolder.get_name() + "\n")

    folders = get_folder_links(startFolder.get_url(), "containerdiv")
    files = get_links(startFolder.get_url(), startFolder.get_name())

    startFolder.add_subfolder(folders)
    startFolder.set_files(files)

    if folders:
        for folder in folders:
            get_all_folders(folder)


def populate_modules(moduleURL):

    # this grabs all the links from the side bar for the module
    links = find_content_link(moduleURL.get_url())

    for link in links:
        get_all_folders(link)

    moduleURL.add_subfolder(links)


def download_module(moduleURL):

    if not os.path.exists(moduleURL.get_name()):
        os.makedirs(moduleURL.get_name())

    os.chdir(moduleURL.get_name())

    if moduleURL.get_files():
        for file in moduleURL.get_files():
            download_file(file)

    if moduleURL.get_subfolders():
        for subfolder in moduleURL.get_subfolders():
            download_module(subfolder)

    os.chdir('..')  # return up a directory


def single_module(inputURL):

    module = bbFolder()

    site = urllib.request.urlopen(inputURL)
    html = site.read()

    # CG - Grab the course name from the module menu title link.
    soup = bs4.BeautifulSoup(html, 'html.parser')
    course_title = soup.find("a", {"id": "courseMenu_link"})

    module.set_name(course_title.text)

    if '/' in module.get_name():
        module.set_name(module_folder.get_name().replace('/', ' '))
        module.set_name(str(module_folder.get_name()).replace(
            '/', '\\'))  # fixes bug of its making extra folder

    module.set_url(inputURL)

    # CG - Parse the content folders for the individual module.
    populate_modules(module)

    print("Module scanned successfully!\n")
    print("Would you like to download all?")

    answer = input("Y/N")

    if("y" in answer.lower()):
        if module.get_subfolders():
            download_module(module)


def scan_modules():

    modules_container = 'https://blackboard.aber.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_55_1'

    modules_folders = get_folder_links(modules_container, 'module:_371_1')

    for module in modules_folders:
        if("vision" in module.get_name().lower()):
            continue
        populate_modules(module)

    print("All modules scanned!\n")

    print("Would you like to download all?")

    answer = input("Y/N")

    if("y" in answer.lower()):
        for module in modules_folders:
            if module.get_subfolders():
                # important to remember that I am passing this as an object
                download_module(module)


def process_input(argv):

    if not argv:

        login_bb_via_stdin()
        scan_modules()

    else:

        try:

            # 'u:' tells getopt that we expect a value for this flag.
            opts, args = getopt.getopt(argv, "hu:", ["url="])

        except getopt.GetoptError:

            print('ERROR - Unexpected input.\nUSAGE: main.py -u <BB URL>')
            sys.exit(2)

        for opt, arg in opts:

            if opt == '-h':
                print('USAGE: main.py [-u|-url=] <BB Module URL>')
                sys.exit()

            else:

                login_bb_via_stdin()

                if opt in ("-u", "--url"):
                    inputURL = arg
                    single_module(inputURL)


def login_bb_via_stdin():

    user = input('Enter Aber ID (e.g. "abc1"): ')
    passwd = getpass.getpass('Enter Password: ')

    login_bb(user, passwd)


def setup():
    user_id_box = 'user_id'
    user_passwd_box = 'password'

    home = expanduser('~/Documents')
    login_bttn = 'login'

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    start_time = time.time()
    os.chdir(home)


def main():

    setup()

    process_input(sys.argv[1:])

    print("\nThanks for using the AberLearn Blackboard downloader!")

if __name__ == "__main__":
    main()
