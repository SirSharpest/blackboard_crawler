################################################
# This is a simple application that will hopefully
# grab pdf's from blackboard and store them on your machine
################################################


################################################
# Imports
################################################
from os.path import expanduser
from time import sleep
import requests
import getpass
from bs4 import BeautifulSoup
from mimetypes import guess_extension
from documents import BBModule, BBFile, BBFolder, get_file



root = 'https://blackboard.aber.ac.uk'


# TODO Refactor
def login_bb_via_stdin():
    user = input('Enter Aber ID (e.g. "abc1"): ')
    passwd = getpass.getpass('Enter Password: ')


"""
Used to recurse down folders
"""
def explore_folder(url, name):
    
    # Change to this directory 
    # And create it 
    
    
    folder = BBFolder(name, url)
    
    # sleep so as not to harass the site
    #sleep(1)    

    try:    
        # navigate to page
        r = s.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        page_content = soup.find(id='content_listContainer')
    except: 
        print('****')
        print(url)
        print(name)
        print('****')
        input('whats happening???')
        
    try:
        # search for folders
        # if we find a folder we search it
        for a in page_content.find_all('a'):
            if is_folder(a['href']):
                u = a['href']
                if 'https' not in u:
                    u = '{0}{1}'.format(root, u)
                folder.add_subfolder(explore_folder(u, a.text))
    except:
        pass
    
    # then search for files
    # and download them
    try:
        for a in page_content.find_all('a'):
            # if it's there then lets create a new file
            if is_file(a.text):
                u = a['href']
                if 'https' not in u:
                    u = '{0}{1}'.format(root, u)
                    folder.add_file(
                            BBFile(a.text, u))
    except:
        pass
    return folder


"""
Checks if url is a bb file
"""
def is_file(text):
    if 'pdf' in text or 'ppt' in text:
        return True
    return False


""" 
Checks if a url is a bb folder
"""
def is_folder(url):
    if '/webapps/blackboard/content/listContent.jsp' in url:
        return True
    return False


# login
s = requests.Session()
data = {'user_id': 'nah26',
        'password': ''}
s.post('https://blackboard.aber.ac.uk/webapps/login/', data)

# grab module infor
r = s.get('https://blackboard.aber.ac.uk/webapps/')
soup = BeautifulSoup(r.content, 'html.parser')

# find modules
modules = []
for ul in soup.find_all('ul', class_='coursefakeclass'):
    for li in ul.find_all('li'):
        a = li.find('a')
        modules.append(
            BBModule(a.contents[1].rsplit(':')[-1].strip(), a['href']))


# for each module
# create tree structure

for m in modules:

    # create root folder
    root_folder = BBFolder('root', m.get_url())
    m.add_folder(root_folder)

    # navigate to module page
    r = s.get('{0}{1}'.format(root, m.get_url()))
    soup = BeautifulSoup(r.content, 'html.parser')

    # find content link
    content_link = ''
    side_menu = soup.find(class_='courseMenu')
    for a in side_menu.find_all('a'):
        if 'Content' in a.contents[0]:
            content_link = a['href']
            break

    # navigate to content link
    r = s.get('{0}{1}'.format(root, content_link))
    soup = BeautifulSoup(r.content, 'html.parser')

    # Now we gotta classify everything as either a file or folder
    # and go over recursively

    page_content = soup.find(id='content_listContainer')
    for a in page_content.find_all('a'):
        if is_folder(a['href']):
            m.add_folder(explore_folder(
                '{0}{1}'.format(root, a['href']), a.text))
            

    # Check for root files
    for a in page_content.find_all('a'):
        # if it's there then lets create a new file
        if is_file(a.text):
            root_folder.add_file(
                BBFile(a.text, '{0}{1}'.format(root, a['href'])))



# then download everything

def searchFolder(folder):
    for f in folder.get_subfolders():
        searchFolder(f)
        
    for f in folder.get_files():
        print(f)
                    
        
for m in modules:
    for f in m.get_folders():
        searchFolder(f)



# change directories
#home = expanduser('~/Documents')
# os.chdir(home)
#
# Generate list of modules
# Currently this page redirects to current modules
#modules_page = requests.get('https://blackboard.aber.ac.uk/webapps/')
#modlues_page_html = bs4.BeautifulSoup(modules_page.content, 'html.parser')
# print(modlues_page_html.find_all('li'))
