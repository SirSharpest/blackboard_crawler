class blackboard_link:
    def __init__(self):
        self.name = None
        self.url = None
        self.recuse = None

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def set_recurse(self, recuse):
        self.recuse = recuse

    def get_recurse(self):
        return self.recuse