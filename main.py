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
import blackboard_loader
from os.path import expanduser
import time
from blackboard_link import blackboard_link

################################################
# global vars (plz don't shout at me)
################################################
user_id_box = 'user_id'
user_passwd_box = 'password'

user = input('Enter in Aber ID')
passwd = input('Enter password')
home = expanduser("~/Documents")
login_bttn = 'login'

################################################
# Main
################################################


#Just doing some setup stuff
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
start_time = time.time()
os.chdir(home)


################################################
# Functions
###############################################

#Grab and download one module's files
def get_module(blackboard_link):
        if not os.path.exists(blackboard_link.get_name()):
            print('Making directory for: ' + blackboard_link.get_name())
            os.makedirs(blackboard_link.get_name())

        if blackboard_link.get_recurse() == True:
            links = blackboard_loader.get_recursive_links(blackboard_link.get_url())
        else:
            links = blackboard_loader.get_links(blackboard_link.get_url())

        os.chdir(blackboard_link.get_name())

        for file in links:
            # Call to download the file
            blackboard_loader.download_pdf(file)

        os.chdir('..')


def get_all(url):
    files = blackboard_loader.get_links(url)
    folders = blackboard_loader.get_folder_links(url, 'content')

    for i in folders:
        print(i.get_name())

    if folders:
        for folder in folders:
            if not os.path.exists(folder.get_name()):
                print('Making sub-folder for:'+folder.get_name())
                os.makedirs(folder.get_name())
            os.chdir(folder.get_name())
            get_all(folder.get_url())
            os.chdir('..')

    for item in files:
        print(item.get_url() + ' found at: ' + url )
        print('Downloading now')
        blackboard_loader.download_pdf(item)


def explore_pages(pages):
    for links in pages:
        if not os.path.exists(links.get_name()):
            print('Making directory for: ' + links.get_name())
            os.makedirs(links.get_name())
        os.chdir(links.get_name())
        get_all(links.get_url())
        os.chdir(home)


#Call to login to blackboard
blackboard_loader.login_bb(user, passwd)


compsci_2nd_year = 'https://blackboard.aber.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_55_1'
compsci_2nd_year_folders = blackboard_loader.get_folder_links(compsci_2nd_year, 'module:_371_1')

for link in compsci_2nd_year_folders:
    link.set_url(blackboard_loader.find_content_link(link.get_url()))

explore_pages(compsci_2nd_year_folders)

end_time = time.time()
total_time = end_time - start_time
print('Finished in: ' + str(total_time) + ' seconds')

