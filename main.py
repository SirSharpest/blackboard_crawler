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
from threading import Thread

################################################
# global vars (plz don't shout at me)
################################################
user_id_box = 'user_id'
user_passwd_box = 'password'

user = input('Enter in Aber ID')
passwd = input('Enter password')
home = expanduser('~/Documents')
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

    Threads = []
    for item in files:

        t = Thread(blackboard_loader.download_file(item))
        Threads.append(t)

        #print(item.get_url() + ' found at: ' + url )
        #print('Downloading now')
        #blackboard_loader.download_file(item)

    for t in Threads:
        t.start()

    for t in Threads:
        t.join()


def explore_pages(pages):
    for links in pages:
        if not links.get_url(): #if the link hasn't been picked up then gloss over it (hopefully)
            continue
        if not os.path.exists(links.get_name()):
            print('Making directory for: ' + links.get_name())
            os.makedirs(links.get_name())
        os.chdir(links.get_name())
        get_all(links.get_url())
        if not os.listdir('../'+links.get_name()):
            os.chdir('../')
            os.rmdir(links.get_name())
        os.chdir(home)



# Call to login to blackboard
blackboard_loader.login_bb(user, passwd)


modules_container = 'https://blackboard.aber.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_55_1'
modules_folders = blackboard_loader.get_folder_links(modules_container, 'module:_371_1')

for link in modules_folders:
    link.set_url(blackboard_loader.find_content_link(link.get_url()))

explore_pages(modules_folders)





end_time = time.time()
total_time = end_time - start_time
print('Finished in: ' + str(total_time) + ' seconds')

