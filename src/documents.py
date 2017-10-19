class BBModule:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.folders = []

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def add_folder(self, folder):
        self.folders.append(folder)

    def get_folders(self):
        return self.folders
    
    

class BBFile:
    def __init__(self, name, url):
        self.name = name.replace('ascii', '').strip()
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url


class BBFolder:
    def __init__(self,name, url):
        self.name = name
        self.url = url
        self.subfolders = []
        self.files = []

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def add_subfolder(self, BBFolder):
        self.subfolder.append(BBFolder)

    def get_subfolders(self):
        return self.subfolders

    def add_file(self, BBFile):
        self.files.append(BBFile)

    def get_files(self):
        return self.files
    
    
# Does just that, finds a file pdf,ppt or pptx and saves it
def get_file(file_to_get):

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
