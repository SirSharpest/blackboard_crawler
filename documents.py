class pdfFile:
    def __init__(self):
        self.name = None
        self.url = None

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url


class bbFolder:
    def __init__(self):
        self.name = None
        self.url = None
        self.subfolders = []

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def add_subfolder(self, bbFolder):
        self.subfolders.append(bbFolder)

    def get_subfolders(self):
        return self.subfolders