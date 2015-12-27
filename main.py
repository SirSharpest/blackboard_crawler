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

################################################
# global vars (plz don't shout at me
################################################
user_id_box = 'user_id'
user_passwd_box = 'password'

user = input('enter your username (aber)')
passwd = input('enter your password ')
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


#Call to login to blackboard
blackboard_loader.login_bb(user, passwd)

#For testing I will be searching this url and attempting to get all from it
ai_content_page = 'https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12907_1&content_id=_665124_1'
cunix_content_page = 'https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12900_1&content_id=_558437_1'
data_structures_content_page = 'https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12896_1&content_id=_674066_1'
software_dev_page = 'https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12897_1&content_id=_668810_1'
persis_data_page = 'https://blackboard.aber.ac.uk/webapps/blackboard/content/listContent.jsp?course_id=_12910_1&content_id=_559019_1&mode=reset'
########################################################
if not os.path.exists('AI Notes'):
    os.makedirs('AI Notes')
    print('Making directory for AI')

links = blackboard_loader.get_links(ai_content_page)
os.chdir('AI Notes')

for file in links:
    #Call to download the file
    blackboard_loader.download_pdf(file)

#########################################################
os.chdir('..')

if not os.path.exists('C & Unix Notes'):
    os.makedirs('C & Unix Notes')
    print('Making directory for C & Unix')

os.chdir('C & Unix Notes')

links = blackboard_loader.get_links(cunix_content_page)

for file in links:
    #Call to download the file
    blackboard_loader.download_pdf(file)

#########################################################
os.chdir('..')

if not os.path.exists('Data Structures Notes'):
    os.makedirs('Data Structures Notes')
    print('Making directory for Data Structures')

os.chdir('Data Structures Notes')

links = blackboard_loader.get_links(data_structures_content_page)

for file in links:
    #Call to download the file
    blackboard_loader.download_pdf(file)

#########################################################
os.chdir('..')

if not os.path.exists('Software Lifecycle'):
    os.makedirs('Software Lifecycle')
    print('Making directory for Software Lifecycle')

os.chdir('Software Lifecycle')

links = blackboard_loader.get_links(software_dev_page)

for file in links:
    #Call to download the file
    blackboard_loader.download_pdf(file)

    #########################################################
os.chdir('..')

if not os.path.exists('Modelling Persistent Data'):
    os.makedirs('Modelling Persistent Data')
    print('Making directory for Modelling Persistent Data')

os.chdir('Modelling Persistent Data')

print('Attempting to find all links in Persistent Data')
links = blackboard_loader.get_recursive_links(persis_data_page)


for file in links:
    #Call to download the file
    blackboard_loader.download_pdf(file)

end_time = time.time()
total_time = end_time - start_time
print('Finished in: ' + str(total_time) + ' seconds')