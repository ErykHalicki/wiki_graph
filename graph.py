from node import node
from collections import deque

prefix = 'https://en.wikipedia.org/wiki/'

class graph:
    def __init__(self, start_link):
        self.start_link = start_link
        self.root = node(start_link)

    def bfs(self, max_depth):
        visited = set()
        unvisited_set = set()
        unvisited = deque()
        unvisited.append(self.root)
        iteration = 0
        while(unvisited[0].depth < max_depth):
            current_page = unvisited.popleft()
            visited.add(current_page.link)
            current_page.get_all_neighbors()
            unvisited_neighbors = [neighbor for neighbor in current_page.neighbors if neighbor.link not in visited and neighbor.link not in unvisited_set]
            unvisited.extend(unvisited_neighbors)
            unvisited_neighbor_links = [neighbor.link for neighbor in unvisited_neighbors]
            unvisited_set.update(unvisited_neighbor_links)
            print(f"{current_page.link} Stats: ")
            print(f"Depth: {current_page.depth}")
            print(f"\t{len(unvisited_neighbors)} / {len(current_page.neighbors)} or {100.0 * len(unvisited_neighbors)/len(current_page.neighbors)}%  neighbors are unvisited in current page")
            print(f"\tLength of unvisited page list at iteration {iteration} is {len(unvisited)}")
            iteration += 1

if __name__ == "__main__":
    g = graph("Dog")
    g.bfs(5)
