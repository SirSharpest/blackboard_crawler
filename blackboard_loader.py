import urllib.request
import urllib.parse
import bs4
from mimetypes import guess_extension
from documents import pdfFile, bbFolder
import re




################################################
# Functions
################################################


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
    print('Accessing: ' + file_to_get.get_name())
    source = urllib.request.urlopen(file_to_get.get_url())
    extension = guess_extension(source.info()['Content-Type'])

    if extension:
        app_name = file_to_get.get_name().encode('utf-8')
        file = open(app_name, 'wb')
        file.write(source.read())
        file.close()
    else:
        file = open('test.pdf', 'wb')
        file.write(source.read())
        file.close()
    print('File saved: ' + file_to_get.get_name())


# This will print the links which have "pdf" specified in the naming
def get_links(url):
    site = urllib.request.urlopen(url)
    html = site.read()
    # parse the html
    soup = bs4.BeautifulSoup(html, 'html.parser')

    data = soup.find_all(id='content')

    # container for the docs
    documents = []

    for div in data:
        links = div.find_all('a')
        for a in links:
            if 'pdf' in a.text.lower() or 'ppt' in a.text.lower() or 'pptx' in a.text.lower() or '.zip' in a.text.lower() or '.class' in a.text.lower():
                temp_doc = pdfFile()
                temp_doc.set_name(a.text)
                temp_doc.set_url('https://blackboard.aber.ac.uk' + a['href'])
                if 'dcswww' in temp_doc.get_url():  # ignore if its on the aber server as cannot access
                    continue
                if 'http://www.cokeandcode.com/main/tutorials/path-finding/' in temp_doc.get_name():  # messy fix needs corrected soon
                    continue
                documents.append(temp_doc)

    return documents


def get_folder_links(url, div):
    site = urllib.request.urlopen(url)
    html = site.read()

    # parse the html
    soup = bs4.BeautifulSoup(html, 'html.parser')

    data = soup.find_all(id=div)

    # container for the docs
    documents = []

    # messy temp variable to avoid confusion with for loop
    temp = div

    for div in data:
        links = div.find_all('a')
        for a in links:
            if 'listContent' in a['href'] or 'execute' in a['href']:
                folder = bbFolder()
                folder.set_name(a.text)
                if '/' in folder.get_name():
                    folder.set_name(folder.get_name().replace('/', ' '))
                    # folder.set_name(str(folder.get_name()).replace('/', '\\'))  # fixes bug of its making extra folder
                folder.set_url('https://blackboard.aber.ac.uk' + a['href'])

                if temp == 'module:_371_1':
                    module_pattern = re.compile('[a-zA-Z]{2}\d{5}')
                    if module_pattern.search(a.text) is not None:
                        print('Found a module ' + a.text)
                        documents.append(folder)
                    continue


                documents.append(folder)

    return documents


def find_content_link(url):
    site = urllib.request.urlopen(url)
    html = site.read()

    # parse the html
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # data = soup.find_all(id='content')
    data = soup.find_all(id='menuWrap')

    for div in data:
        links = div.find_all('a')
        for a in links:

            #if its not a realitive link then I want to avoid it
            if 'www.' in a['href']:
                continue

            if 'Content' in a.text or 'Course Documents' in a.text or 'Statistics' in a.text or 'Research methods' in a.text:
                return ('https://blackboard.aber.ac.uk' + a['href'])
