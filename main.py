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
import re



################################################
# Functions
###############################################

#  CG - Based on code from original source: https://filippo.io/send-a-head-request-in-python/
class HEADRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    Subclass the HTTPRedirectHandler to make it use our
    HeadRequest also on the redirected URL
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            newurl = newurl.replace(' ', '%20')
            return HeadRequest(newurl,
                               headers=req.headers,
                               origin_req_host=req.origin_req_host,
                               unverifiable=True)
        else:
            raise urllib.error.HTTPError(req.get_full_url(), code, msg, headers, fp)

class HeadRequest(urllib.request.Request):
    def get_method(self):
        return "HEAD"

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
    print('Connected!')


# Does just that, finds a file pdf,ppt or pptx and saves it
def download_file(file_to_get):

    if os.path.isfile(file_to_get.get_name()):
        print(file_to_get.get_name() + " already exists in this directory... skipping it")
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

    # CG - Returns the converted absolute BB url, or returns the original URL unmodified.
    return re.sub(r'^(\/.*)$', r'https://blackboard.aber.ac.uk\1', url)

def resolve_redirect_result_url(originalURL):

    opener = urllib.request.OpenerDirector()

    for handler in [urllib.request.HTTPHandler,
                    urllib.request.HTTPDefaultErrorHandler,
                    urllib.request.HTTPErrorProcessor,
                    urllib.request.HTTPSHandler,
                    HEADRedirectHandler]:

        opener.add_handler(handler())

    response = opener.open(HeadRequest(originalURL))

    # CG - If we have a new URL from the response, return that, otherwise return the orignal URL.

    try:
        return response.geturl()
    except AttributeError:
        return originalURL



def test_file_url_extension(fileURL):

    file_url_match = re.search(r'^(https?\:\/\/blackboard.aber.ac.uk).*\.((?:doc|xls|ppt)x?|pdf|txt|class|zip)$', fileURL.lower())
    # file_url_match = re.search(r'^^(?:https?:\/\/blackboard.aber.ac.uk).*\/(.*\.(?:(?:doc|xls|ppt)x?|pdf|txt|class|zip))$', fileURL.lower())

    # if file_url_match:
        # print(file_url_match.group(1))
        # return file_url_match.group(1)

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

                absolute_href_url = convert_relative_to_absolute_url(a['href'])
                redirect_url = resolve_redirect_result_url(absolute_href_url)

                # new_url = re.sub(r'(?:https://blackboard\.aber\.ac\.uk)|^(\/.*)$', r'https://blackboard.aber.ac.uk\1', a['href'])

                # CG - We can rely on the order of conditionals here for evaluation boolean operators in Python.
                # See: https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not for more information.
                # if test_file_name_extension(a.text) or test_file_url_extension(absolute_href_url):

                if test_file_url_extension(redirect_url):

                    try:

                        temp_doc = pdfFile()

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
                        folder.set_name(str(folder.get_name()).replace('/', '\\'))  # fixes bug of its making extra folder
                    folder.set_url('https://blackboard.aber.ac.uk' + a['href'])

                    if  "listContentEditable" in a['href']:
                        continue

                    if divtag == 'module:_371_1':
                        # CG - Updated REGEX to check for module code pattern EITHER as 'AB12345' or 'ABC1234' (case-insensitive).
                        # CG - Some modules (e.g. Masters) use three letters and four numbers, rather than two letters and five numbers.
                        module_pattern = re.compile('[a-zA-Z]{2}\d{5}|[a-zA-Z]{3}\d{4}')
                        if module_pattern.search(a.text) is not None:
                            print('Found a module ' + a.text)
                            documents.append(folder)
                        continue

                    documents.append(folder)

                if "launchLink" in a['href']:
                    continue
            except:
                print("Oh deer, something broke whilst finding folder links")
                continue

    return documents


#This function should get all of the links in the sidebar
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
        #somethings we want to ignore
        if "panopto" in a.span.text.lower() or "announcements" in a.span.text.lower() or "discussion" \
                in a.span.text.lower() or "aspire" in a.span.text.lower() or "tools" in a.span.text.lower() \
                or "http" in a.text.lower() :
             continue

        if "content"  in a.span.text.lower() or "slides" in a.span.text.lower() \
            or "course" in a.span.text.lower() or "lecture" in a.span.text.lower():

            folder = bbFolder()
            folder.set_name(a.span.text)
            folder.set_url('https://blackboard.aber.ac.uk' + a['href'])

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

    links = find_content_link(moduleURL.get_url())  # this grabs all the links from the side bar for the module

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

    os.chdir('..') # return up a directory


################################################
# Main
################################################


#Just doing some setup stuff

user_id_box = 'user_id'
user_passwd_box = 'password'

user = input('Enter in Aber ID (e.g. "abc1"): ')
passwd = getpass.getpass('Enter Password: ')
home = expanduser('~/Documents')
login_bttn = 'login'


cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
start_time = time.time()
os.chdir(home)


# Call to login to blackboard
login_bb(user, passwd)

modules_container = 'https://blackboard.aber.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_55_1'

modules_folders = get_folder_links(modules_container, 'module:_371_1')


for module in modules_folders:
    if( "vision" in module.get_name().lower() ):
        continue
    populate_modules(module)

print("All modules scanned!")

print("Would you like to download all?")

answer = input("Y/N")

if("y" in answer.lower()):
    for module in modules_folders:
        if module.get_subfolders():
            download_module(module)  # important to remember that I am passing this as an object

print("Thanks for using the blackboard downloader!")
