import requests
from bs4 import BeautifulSoup

class node:
    def __init__(self,link,parent=None, link_limit = 100):
        if(parent != None):
            self.depth = parent.depth+1
        else:
            self.depth = 0
        self.neighbors = []
        self.parent = parent
        self.link = link
        self.prefix = 'https://en.wikipedia.org/wiki/'
        self.link_limit = link_limit

    def valid_link(self, link):
        if (link.startswith('/wiki/')
            and 'Special:' not in link
            and 'Category:' not in link
            and 'Wikipedia:' not in link
            and 'Help:' not in link
            and 'File:' not in link
            and 'Portal:' not in link
            and '(identifier)' not in link
            and 'Main_Page' not in link
            and 'Talk:' not in link
            and '(disambiguation)' not in link
            and 'Template:' not in link
            and link[6:] != self.link):
            return True
        return False

    def get_all_neighbors(self):
        if(len(self.neighbors) != 0):
            return self.neighbors
        try:
            response = requests.get(self.prefix + self.link)
            response.raise_for_status()  # Check for request errors
            soup = BeautifulSoup(response.text, 'html.parser')
            all_neighbors = [node(a['href'][6:],self) for a in soup.find_all('a', href=True) if self.valid_link(a['href'])]
            self.neighbors = all_neighbors[:self.link_limit]
            return self.neighbors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return []
