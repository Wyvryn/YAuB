import re


class Plugin(object):

    def __init__(self):
        self.name = ''
        self.description = ''
        self.regex = []  # List of tuples [(find, replace)]
        self.replace = []  # List of tuples [(find, replace)] - find and replace cannot be regex
        self.header_includes = []  # List of strings to include in page header
        self.footer_includes = []  # List of strings to include in page footer

    def transmute(self, data):
        # This function allows you to mess with the post data as you see fit
        pass

    def run(self, data):
        if data:

            self.transmute(data)

            for find, replace in self.regex:
                if find:
                    data = re.sub(find, replace, data)

            for find, replace in self.replace:
                if find:
                    data = data.replace(find, replace)
        return data
