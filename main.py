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
        print('Accessing: ' + file_to_get.get_name())
        source = urllib.request.urlopen(file_to_get.get_url())
        app_name = file_to_get.get_name().encode('utf-8')
        file = open(app_name, 'wb')
        file.write(source.read())
        file.close()
        print('File saved: ' + file_to_get.get_name())


# This will print the links which have "pdf" specified in the naming
def get_links(url, folderName):
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
            if '.pdf' in a.text.lower() or '.ppt' in a.text.lower() or '.pptx' in a.text.lower() or '.zip' in a.text.lower() or '.class' in a.text.lower():

                try:
                    temp_doc = pdfFile()
                    temp_doc.set_name(a.text)
                    temp_doc.set_url('https://blackboard.aber.ac.uk' + a['href'])
                    if 'dcswww' in temp_doc.get_url():  # ignore if its on the aber server as cannot access
                        continue
                    if 'http://www.cokeandcode.com/main/tutorials/path-finding/' in temp_doc.get_name():  # messy fix needs corrected soon
                        continue
                    documents.append(temp_doc)

                except:
                    print("bork trying to get the address of a file")
                    continue

    return documents


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
                        module_pattern = re.compile('[a-zA-Z]{2}\d{5}')
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

    print("looking at: " + startFolder.get_name() )

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

user = input('Enter in Aber ID: ')
passwd = input('Enter password: ')
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



