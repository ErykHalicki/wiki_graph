import requests
from bs4 import BeautifulSoup


class node:
    def __init__(self, link, parent=None, link_limit=400):
        if(parent != None):
            self.depth = parent.depth+1
        else:
            self.depth = 0
        self.neighbors = []
        self.parent = parent
        self.link = link
        self.prefix = 'https://en.wikipedia.org/wiki/'
        self.link_limit = link_limit
        self.distance=1000 #no 2 pages will ever be 1000 links apart, so this is practically infinity
        self.similarity=1000
        self.link_size = 0 

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

    def get_similarity_to(self, target):
        #this function calculates the estiamted distance between 2 concepts
        #if the return value is low, the 2 links are similar, so we should continue out search in that direction

        #using inverse jaccard similarity of the neighboring node links
        
        node_links, target_links = set([neighbor.link for neighbor in self.neighbors]), set([neighbor.link for neighbor in target.neighbors])
        intersection = node_links.intersection(target_links)
        union = node_links.union(target_links)
        #since we are using inverse jaccard similarity, a high similarity results in a lower score, i.e a lower distance

        self.similarity = (len(union) / len(intersection) - 1) if intersection else 1000

    def get_all_neighbors(self):
        if(len(self.neighbors) != 0):
            return self.neighbors
        try:
            response = requests.get(self.prefix + self.link)
            response.raise_for_status()  # Check for request errors
            soup = BeautifulSoup(response.text, 'html.parser')
            temp_neighbors = set()
            all_neighbors = []
            for a in soup.find_all('a', href=True):
                if self.valid_link(a['href']) and a['href'][6:] not in temp_neighbors:
                    all_neighbors.append(node(a['href'][6:], self))
                    temp_neighbors.add(a['href'][6:])
            self.link_size=len(all_neighbors)
            self.neighbors = all_neighbors[:self.link_limit]
            return self.neighbors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return []

    def __lt__(self, other):
        return (self.distance < other.distance)
