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

pages = []
#For testing I will be searching this url and attempting to get all from it
ai_content_page = blackboard_link()
ai_content_page.set_name('AI')
ai_content_page.set_url('https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12907_1&content_id=_665124_1')

cunix_content_page = blackboard_link()
cunix_content_page.set_name('C & Unix')
cunix_content_page.set_url('https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12900_1&content_id=_542745_1&mode=reset')

data_structures_content_page = blackboard_link()
data_structures_content_page.set_name('Data Structures')
data_structures_content_page.set_url('https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12896_1&content_id=_674066_1')

software_dev_page = blackboard_link()
software_dev_page.set_name('Software Development')
software_dev_page.set_url('https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12897_1&content_id=_668810_1')

persis_data_content_page = blackboard_link()
persis_data_content_page.set_name('Persistent Data')
persis_data_content_page.set_url('https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12910_1&content_id=_559019_1&mode=reset')
persis_data_content_page.set_recurse(True)

# Add these pages to a list to iterate over
pages.append(ai_content_page)
pages.append(cunix_content_page)
pages.append(data_structures_content_page)
pages.append(software_dev_page)
pages.append(persis_data_content_page)

explore_pages(pages)

end_time = time.time()
total_time = end_time - start_time
print('Finished in: ' + str(total_time) + ' seconds')



# compsci_2nd_year = 'https://blackboard.aber.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_55_1'
# compsci_2nd_year_folders = blackboard_loader.get_folder_links(compsci_2nd_year, 'module:_371_1')
#
#
# compsci_2nd_year_folders_content = []
#
# for module in compsci_2nd_year_folders:
#     compsci_2nd_year_folders_content.append(blackboard_loader.find_content_link(module))
#
# for content in compsci_2nd_year_folders_content:
#     tmp = blackboard_link()
#     tmp.set_name('test')
#     tmp.set_url(content)
#     get_all(tmp)
